"""Three alternative renderers for the contribution-city slice.

Each takes the same (calendar, updated) that render.build_city does and returns a
drop-in 880-wide slice, reusing render.py's theme palette, font subsetting and
console frame. Pick one with `render.py --city <name>` once a direction is chosen.

  metropolis  — the iso skyline, but a rain-slick neon downtown: every tower
                mirrored in a wet street, searchlight sweep, depth haze, big moon.
  reactor     — a radial "contribution core": 366 days as a ring of light-bars
                around a glowing reactor, radar sweep, month spokes.
  circuit     — a printed-circuit board: 12 month-chips wired in a data bus,
                each day a solder pad lit by that day's activity, gold edge connector.

Rendered static by rsvg-convert (animations are a live-README bonus), so every
piece reads fully at rest.
"""
import datetime, json, math

import render as R


def _days(calendar):
    return [(datetime.date.fromisoformat(d), n) for d, n in calendar]


# ═══════════════════════════════ 1 · metropolis ═══════════════════════════════
def _tower(cx, cy, h, level, rnd, roof=None, flick=False):
    """One isometric tower (two faces + roof + windows) at ground-centre (cx, cy).

    roof overrides the roof colour (used to crown the peak day); flick lets a few
    windows blink for life in the live README.
    """
    TW, TH, p = R.CITY_TW, R.CITY_TH, R._p
    L, Rr = (cx - TW / 2, cy), (cx + TW / 2, cy)
    T, B = (cx, cy - TH / 2), (cx, cy + TH / 2)
    Tu, Ru, Bu, Lu = [(x, y - h) for x, y in (T, Rr, B, L)]
    s = [f'<path d="M{p(*L)}L{p(*B)}L{p(*Bu)}L{p(*Lu)}Z" fill="{R.FACE_L}"/>'
         f'<path d="M{p(*B)}L{p(*Rr)}L{p(*Ru)}L{p(*Bu)}Z" fill="{R.FACE_R}"/>'
         f'<path d="M{p(*Tu)}L{p(*Ru)}L{p(*Bu)}L{p(*Lu)}Z" fill="{roof or R.ROOFS[level]}"/>']
    on, side, off, fl = [], [], [], []
    for face, (a, b) in (("l", (L, B)), ("r", (B, Rr))):
        for r in range(int((h - 6) // 7)):
            v0 = 5 + r * 7
            for u0 in (.18, .58):
                lit = next(rnd) < .6
                if not lit and next(rnd) < .5:
                    continue
                pts = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - v)
                       for u, v in ((u0, v0), (u0 + .26, v0), (u0 + .26, v0 + 3.2), (u0, v0 + 3.2))]
                seg = "M" + "L".join(p(*q) for q in pts) + "Z"
                if not lit:
                    off.append(seg)
                elif flick and next(rnd) < .06:
                    fl.append((seg, face))
                else:
                    (on if face == "l" else side).append(seg)
    if off:
        s.append(f'<path d="{"".join(off)}" fill="{R.WIN_OFF}"/>')
    if on:
        s.append(f'<path d="{"".join(on)}" fill="{R.WIN_ON}"/>')
    if side:
        s.append(f'<path d="{"".join(side)}" fill="{R.WIN_ON_SIDE}"/>')
    for i, (seg, face) in enumerate(fl):
        s.append(f'<path class="f{i%3}" d="{seg}" fill="{R.WIN_ON if face == "l" else R.WIN_ON_SIDE}"/>')
    return "".join(s)


def build_metropolis(calendar, updated, as_parts=False):
    CY, MG, GR, AM, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    lv = R._levels(counts)
    rnd = R._rng(f"{updated}-{total}-metro")
    start = days[0][0]

    OX, OY, TW, TH, HMAX = 150, 258, R.CITY_TW, R.CITY_TH, 138
    cells = []
    for d, n in days:
        idx = (d - start).days
        cells.append((idx // 7, (d.weekday() + 1) % 7, n, d))
    cells.sort(key=lambda c: (c[0] + c[1], c[0]))               # back to front

    busiest_d, busiest_n = max(days, key=lambda t: t[1])

    towers, reflections, peak_xy = [], [], None
    for w, dow, n, d in cells:
        if n == 0:
            continue
        cx = OX + (w - dow) * TW / 2
        cy = OY + (w + dow) * TH / 2
        h = 10 + (HMAX - 10) * math.sqrt(n / peak)
        level = sum(n > t for t in lv)
        is_peak = d == busiest_d
        mk = _tower(cx, cy, h, level, rnd, roof=AM if is_peak else None, flick=not is_peak)
        plural = "" if n == 1 else "s"
        towers.append(f'<g><title>{d:%b %-d, %Y} · {n} contribution{plural}</title>{mk}</g>')
        reflections.append(f'<g transform="translate(0 {2*cy:.1f}) scale(1 -1)" opacity=".2">{mk}</g>')
        if is_peak:
            peak_xy = (cx, cy, h)

    # sky — twinkling stars, a haloed moon, a searchlight sweep, soft rain
    stars = []
    for i in range(54):
        x, y = FL + 20 + next(rnd) * (FR - FL - 40), 120 + next(rnd) * 120
        if 630 < x < 760 and y < 210:
            continue
        cls = f' class="s{i%3}"' if i % 3 == 0 else ""
        stars.append(f'<circle{cls} cx="{x:.1f}" cy="{y:.1f}" r="{(.6,.9,1.2)[i%3]}" fill="#dfe8f0" opacity="{.3+next(rnd)*.5:.2f}"/>')
    moonx, moony = FR - 94, 152                                 # top-right, clear of the text column
    rain = "".join(f'<line class="rn{i%3}" x1="{(rx:=FL+next(rnd)*(FR-FL)):.1f}" y1="{(ry:=130+next(rnd)*340):.1f}" x2="{rx-6:.1f}" y2="{ry+22:.1f}" stroke="{CY}" stroke-width="1" stroke-opacity=".16"/>'
                    for i in range(44))
    searchlight = (f'<g class="sweep" style="transform-origin:470px 560px">'
                   f'<path d="M470 560L360 150L580 150Z" fill="url(#beam)" opacity=".42"/></g>')

    # peak-day crown: spotlight column + blinking rooftop beacon + a flag label
    peak_svg = ""
    if peak_xy:
        pcx, pcy, ph = peak_xy
        apex = pcy - ph - TH / 2                                # roof top point
        right = pcx < FR - 150
        lxx, anc = (pcx + 22, "start") if right else (pcx - 22, "end")
        flag = f'M{pcx:.1f} {apex-30:.1f}l{16 if right else -16} 5l{-16 if right else 16} 5Z'
        peak_svg = (
            f'<path d="M{pcx-9:.1f} {apex-128:.1f}L{pcx+9:.1f} {apex-128:.1f}L{pcx+34:.1f} {apex+6:.1f}L{pcx-34:.1f} {apex+6:.1f}Z" fill="url(#spot)"/>'
            f'<line x1="{pcx:.1f}" y1="{apex:.1f}" x2="{pcx:.1f}" y2="{apex-30:.1f}" stroke="{AM}" stroke-width="1.4"/>'
            f'<path d="{flag}" fill="{AM}"/>'
            f'<circle class="beacon" cx="{pcx:.1f}" cy="{apex-30:.1f}" r="3.6" fill="{MG}" filter="url(#g)"/>'
            f'<circle class="beacon" cx="{pcx:.1f}" cy="{apex-30:.1f}" r="2.4" fill="#fff"/>'
            f'<text x="{lxx:.1f}" y="{apex-28:.1f}" text-anchor="{anc}" font-weight="800" fill="{AM}" letter-spacing="2" style="font-size:14px">PEAK</text>'
            f'<text x="{lxx:.1f}" y="{apex-13:.1f}" text-anchor="{anc}" class="dim" style="font-size:11px">{busiest_d:%b %-d} · {busiest_n}</text>')

    fy = 648
    info = [f'<tspan class="cy" font-weight="700">{total:,}</tspan> contributions',
            f'last 365 days',
            f'busiest <tspan class="fg">{busiest_d:%b} {busiest_d.day}</tspan> · {busiest_n} in a day',
            f'{sum(1 for n in counts if n)} nights lit']
    info_svg = "".join(f'<text x="{X}" y="{150+i*20}" class="dim" style="font-size:12px">{t}</text>'
                       for i, t in enumerate(info))
    legend = "".join(f'<rect x="{X+52+i*16}" y="642" width="11" height="11" fill="{c}"/>'
                     for i, c in enumerate([R.EMPTY_DAY] + R.ROOFS))

    body = R.heading(44, "contribution-metropolis", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> render-city --neon --reflections <tspan fill="#484f58"># rain never stops downtown</tspan></text></g>
<g>{"".join(stars)}</g>
<circle cx="{moonx}" cy="{moony}" r="54" fill="url(#moonglow)"/>
<circle cx="{moonx}" cy="{moony}" r="17" fill="#eef4fb"/>
<circle cx="{moonx+6}" cy="{moony-5}" r="15" fill="{BG}"/>
{searchlight}
<g opacity=".9">{"".join(reflections)}</g>
<rect x="{FL}" y="470" width="{FR-FL}" height="{690-470}" fill="url(#wet)"/>
<g>{"".join(towers)}</g>
{peak_svg}
<g clip-path="url(#cityclip)">{rain}</g>
<rect x="{FL}" y="{fy}" width="{FR-FL}" height="2" fill="{CY}" opacity=".35" filter="url(#g)"/>
{info_svg}
<text x="{X}" y="652" class="dim" style="font-size:11px">quiet</text>{legend}<text x="{X+52+5*16+6}" y="652" class="dim" style="font-size:11px">skyscraper</text>'''
    css = f"""@keyframes tw{{0%,100%{{opacity:.9}}50%{{opacity:.15}}}}
@keyframes sweep{{0%{{transform:rotate(-16deg)}}50%{{transform:rotate(18deg)}}100%{{transform:rotate(-16deg)}}}}
@keyframes fl{{0%,40%,100%{{opacity:1}}45%,60%{{opacity:.08}}}}
@keyframes beaconb{{0%,84%,100%{{opacity:1}}42%{{opacity:.12}}}}
@keyframes rain{{from{{transform:translate(0,-30px)}}to{{transform:translate(-120px,420px)}}}}
.s0{{animation:tw 3s infinite}}
.sweep{{animation:sweep 11s ease-in-out infinite}}
.f0{{animation:fl 5s infinite}}.f1{{animation:fl 7s infinite 2s}}.f2{{animation:fl 9s infinite 4s}}
.beacon{{animation:beaconb 1.6s ease-in-out infinite}}
.rn0{{animation:rain 1.1s linear infinite}}.rn1{{animation:rain 1.5s linear infinite}}.rn2{{animation:rain .85s linear infinite}}"""
    defs = (f'<radialGradient id="moonglow"><stop offset="0" stop-color="#eef4fb" stop-opacity=".28"/><stop offset="1" stop-color="#eef4fb" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="wet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".55" stop-color="{BG}" stop-opacity=".55"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient>'
            f'<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity=".5"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="spot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AM}" stop-opacity="0"/><stop offset="1" stop-color="{AM}" stop-opacity=".18"/></linearGradient>'
            f'<clipPath id="cityclip"><rect x="{FL}" y="110" width="{FR-FL}" height="540"/></clipPath>')
    desc = (f"Contribution city at night, rendered as a rain-slick neon downtown: one tower per active day of the last year, "
            f"taller and brighter for busier days, each mirrored in the wet street under a searchlight and a full moon. "
            f"{total:,} contributions, busiest day {busiest_d:%B} {busiest_d.day} with {busiest_n}.")
    text = ("~/contribution-metropolis// 02$ render-city --neon --reflections # rain never stops downtown"
            "quietskyscrapercontributions last 365 days busiest in a day nights lit")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution city — neon downtown", desc=desc,
                       text=text, css=css, defs=defs)


# ═══════════════════════════════ 3 · reactor ══════════════════════════════════
def build_reactor(calendar, updated, as_parts=False):
    CY, MG, GR, AM, VI, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.VIOLET, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    lv = R._levels(counts)
    busiest_i, (busiest_d, busiest_n) = max(enumerate(days), key=lambda t: t[1][1])
    active = sum(1 for n in counts if n)
    longest_streak = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest_streak = max(longest_streak, run)
    cur_streak = 0
    for n in reversed(counts):
        if not n:
            break
        cur_streak += 1
    # monthly totals (last 12 calendar months) for the left HUD bar chart
    months = []
    for d, n in days:
        k = (d.year, d.month)
        if not months or months[-1][0] != k:
            months.append([k, 0])
        months[-1][1] += n
    months = months[-12:]
    mmax = max((m for _, m in months), default=1) or 1

    cx0, cy0 = 440, 392
    r_core, L_max = 76, 190
    ring_cols = R.ROOFS[1:] + [R.WIN_ON]                        # 4 brightness steps
    N = len(days)

    # faint guide rings + radial month grid
    guides = []
    for f in (0, .33, .66, 1.0):
        guides.append(f'<circle cx="{cx0}" cy="{cy0}" r="{r_core+L_max*f:.1f}" fill="none" stroke="{CY}" stroke-opacity=".12"/>')
    # month spokes + labels
    spokes, start = [], days[0][0]
    seen = set()
    for i, (d, _) in enumerate(days):
        key = (d.year, d.month)
        if d.day > 3 or key in seen:
            continue
        seen.add(key)
        ang = math.radians(-90 + i / N * 360)
        ca, sa = math.cos(ang), math.sin(ang)
        x1, y1 = cx0 + r_core * ca, cy0 + r_core * sa
        x2, y2 = cx0 + (r_core + L_max) * ca, cy0 + (r_core + L_max) * sa
        lx, ly = cx0 + (r_core + L_max + 16) * ca, cy0 + (r_core + L_max + 16) * sa
        spokes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{CY}" stroke-opacity=".08"/>'
                      f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="middle" class="dim" style="font-size:10px">{d:%b}</text>')

    # the 366 day-bars (the peak ray is skipped here and crowned on top)
    bars, glows = [], []
    for i, (d, n) in enumerate(days):
        ang = math.radians(-90 + i / N * 360)
        ca, sa = math.cos(ang), math.sin(ang)
        length = 4 + (L_max - 4) * math.sqrt(n / peak) if n else 3
        r1 = r_core + 2
        x1, y1 = cx0 + r1 * ca, cy0 + r1 * sa
        x2, y2 = cx0 + (r1 + length) * ca, cy0 + (r1 + length) * sa
        if n == 0:
            bars.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{R.EMPTY_DAY}" stroke-width="2"/>')
            continue
        if i == busiest_i:
            continue
        level = sum(n > t for t in lv)
        col = ring_cols[level]
        plural = "" if n == 1 else "s"
        bars.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.3" stroke-linecap="round"><title>{d:%b %-d, %Y} · {n} contribution{plural}</title></line>')
        if level >= 2:
            glows.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.3" stroke-linecap="round"/>')

    # the peak ray — amber, thick, haloed, with a pulsing tip and a flag label
    ang = math.radians(-90 + busiest_i / N * 360)
    ca, sa = math.cos(ang), math.sin(ang)
    ix, iy = cx0 + (r_core + 2) * ca, cy0 + (r_core + 2) * sa
    pr = r_core + 2 + (L_max - 4) * math.sqrt(busiest_n / peak)
    bx, by = cx0 + pr * ca, cy0 + pr * sa
    lx, ly = cx0 + (pr + 28) * ca, cy0 + (pr + 28) * sa
    anc = "end" if ca < -0.2 else ("start" if ca > 0.2 else "middle")
    peak_mark = (
        f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{AM}" stroke-width="3.6" stroke-linecap="round" filter="url(#g)"/>'
        f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{AM}" stroke-width="3.4" stroke-linecap="round"><title>busiest · {busiest_d:%b %-d, %Y} · {busiest_n} contributions</title></line>'
        f'<circle class="ping" cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="none" stroke="{AM}" stroke-width="1.6"/>'
        f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="3.4" fill="{AM}"/>'
        f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="1.8" fill="#fff"/>'
        f'<text x="{lx:.1f}" y="{ly-2:.1f}" text-anchor="{anc}" font-weight="800" fill="{AM}" letter-spacing="2" style="font-size:13px">PEAK</text>'
        f'<text x="{lx:.1f}" y="{ly+12:.1f}" text-anchor="{anc}" class="dim" style="font-size:11px">{busiest_d:%b %-d} · {busiest_n}</text>')

    # radar sweep wedge (rotates in the live README, rests here)
    sweep = (f'<g class="radar" style="transform-origin:{cx0}px {cy0}px">'
             f'<path d="M{cx0} {cy0}L{cx0+r_core+L_max} {cy0}A{r_core+L_max} {r_core+L_max} 0 0 0 {cx0+(r_core+L_max)*math.cos(math.radians(-32)):.1f} {cy0+(r_core+L_max)*math.sin(math.radians(-32)):.1f}Z" fill="url(#radar)"/></g>')

    core = (f'<circle cx="{cx0}" cy="{cy0}" r="{r_core+34}" fill="url(#coreglow)"/>'
            f'<circle cx="{cx0}" cy="{cy0}" r="{r_core}" fill="{BG}" stroke="{CY}" stroke-opacity=".5"/>'
            f'<circle class="pulse" cx="{cx0}" cy="{cy0}" r="{r_core-7}" fill="none" stroke="{CY}" stroke-opacity=".35"/>'
            f'<circle cx="{cx0}" cy="{cy0}" r="13" fill="{CY}" filter="url(#g)"/>'
            f'<circle cx="{cx0}" cy="{cy0}" r="7" fill="#eafcff"/>'
            f'<text x="{cx0}" y="{cy0-4}" text-anchor="middle" font-weight="800" class="wh" style="font-size:30px">{total:,}</text>'
            f'<text x="{cx0}" y="{cy0+16}" text-anchor="middle" letter-spacing="2" class="cy" style="font-size:11px">CONTRIBUTIONS</text>'
            f'<text x="{cx0}" y="{cy0+34}" text-anchor="middle" class="dim" style="font-size:11px">last 365 days</text>')

    # left HUD — monthly throughput bars (fills the left margin with real data)
    hud = [f'<text x="34" y="150" letter-spacing="2" class="dim" style="font-size:10.5px">MONTHLY FLOW</text>']
    for mi, ((yr, mo), msum) in enumerate(months):
        yy = 168 + mi * 32
        bw = 5 + 78 * (msum / mmax)
        lab = datetime.date(yr, mo, 1).strftime("%b")
        lvl = 3 if msum >= mmax * .66 else (2 if msum >= mmax * .33 else 1)
        hud.append(f'<text x="34" y="{yy+8:.0f}" class="dim" style="font-size:10px">{lab}</text>'
                   f'<rect x="66" y="{yy:.0f}" width="{bw:.1f}" height="9" fill="{ring_cols[lvl]}" fill-opacity=".85"/>'
                   f'<text x="{66+bw+5:.1f}" y="{yy+8:.0f}" class="dim" style="font-size:9px">{msum}</text>')
    hud_svg = "".join(hud)

    # right HUD — headline readouts + intensity legend (fills the right margin)
    rx = FR - 36
    read = [("TOTAL", f"{total:,}"), ("ACTIVE", f"{active}/{N}d"),
            ("STREAK", f"{cur_streak}d"), ("LONGEST", f"{longest_streak}d")]
    rsvg = []
    for ri, (k, v) in enumerate(read):
        yy = 162 + ri * 52
        rsvg.append(f'<text x="{rx}" y="{yy}" text-anchor="end" letter-spacing="1.5" class="dim" style="font-size:10px">{k}</text>'
                    f'<text x="{rx}" y="{yy+23}" text-anchor="end" font-weight="800" class="wh" style="font-size:21px">{v}</text>')
    ly0 = 162 + 4 * 52 + 8
    rsvg.append(f'<text x="{rx}" y="{ly0}" text-anchor="end" letter-spacing="1.5" class="dim" style="font-size:10px">INTENSITY</text>')
    for i, (c, nm) in enumerate(zip([R.EMPTY_DAY] + ring_cols, ["quiet", "low", "mid", "high", "peak"])):
        rsvg.append(f'<rect x="{rx-11}" y="{ly0+10+i*18}" width="11" height="11" fill="{c}"/>'
                    f'<text x="{rx-18}" y="{ly0+20+i*18}" text-anchor="end" class="dim" style="font-size:10px">{nm}</text>')
    right_svg = "".join(rsvg)

    body = R.heading(44, "contribution-reactor", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> reactor --spin 366d <tspan fill="#484f58"># one ray per day, out from the core</tspan></text></g>
<g>{"".join(guides)}</g>
<g>{"".join(spokes)}</g>
{sweep}
<g class="rays"><g filter="url(#g)" opacity=".7">{"".join(glows)}</g>
<g>{"".join(bars)}</g></g>
{peak_mark}
{core}
{hud_svg}
{right_svg}'''
    css = f"""@keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
@keyframes corepulse{{0%,100%{{transform:scale(1);opacity:.35}}50%{{transform:scale(1.5);opacity:0}}}}
@keyframes ping{{0%{{r:5;opacity:1}}100%{{r:22;opacity:0}}}}
@keyframes breathe{{0%,100%{{transform:scale(.955)}}50%{{transform:scale(1.05)}}}}
.radar{{animation:spin 8s linear infinite}}
.pulse{{transform-origin:{cx0}px {cy0}px;animation:corepulse 3.2s ease-out infinite}}
.ping{{animation:ping 2.4s ease-out infinite}}
.rays{{transform-origin:{cx0}px {cy0}px;animation:breathe 3.8s ease-in-out infinite}}"""
    defs = (f'<radialGradient id="coreglow"><stop offset="0" stop-color="{CY}" stop-opacity=".45"/><stop offset=".6" stop-color="{CY}" stop-opacity=".12"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="radar" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({cx0} {cy0}) scale({r_core+L_max})"><stop offset="0" stop-color="{CY}" stop-opacity=".0"/><stop offset=".7" stop-color="{CY}" stop-opacity=".02"/><stop offset="1" stop-color="{CY}" stop-opacity=".10"/></radialGradient>')
    desc = (f"Contribution reactor: the last year drawn as 366 light-rays spun out from a glowing core, "
            f"each ray longer and brighter for a busier day, with month spokes and a radar sweep. "
            f"{total:,} contributions, {active} active days, busiest {busiest_d:%B} {busiest_d.day} with {busiest_n}.")
    text = ("~/contribution-reactor// 02$ reactor --spin 366d # one ray per day, out from the core"
            "CONTRIBUTIONSlast 365 days MONTHLY FLOW TOTAL ACTIVE STREAK LONGEST INTENSITY"
            "quiet low mid high peak PEAK JanFebMarAprMayJunJulAugSepOctNovDec")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution reactor", desc=desc,
                       text=text, css=css, defs=defs)


# ═══════════════════════════════ 4 · circuit ══════════════════════════════════
def build_circuit(calendar, updated, as_parts=False):
    CY, MG, GR, AM, VI, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.VIOLET, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    lv = R._levels(counts)
    active = sum(1 for n in counts if n)
    busiest_d, busiest_n = max(days, key=lambda t: t[1])
    pad_cols = R.ROOFS[1:] + [R.WIN_ON]

    # group the trailing year into calendar months, in order
    months = []
    for d, n in days:
        key = (d.year, d.month)
        if not months or months[-1][0] != key:
            months.append((key, []))
        months[-1][1].append((d, n))
    months = months[-12:]                                      # last 12 month-chips

    board = f'{R.FACE_R}'
    # board substrate + silkscreen via grid
    gx0, gy0, gx1, gy1 = FL + 20, 150, FR - 20, 636
    vias = []
    for yy in range(gy0 + 16, gy1, 34):
        for xx in range(gx0 + 16, gx1, 34):
            vias.append(f'<circle cx="{xx}" cy="{yy}" r="1.1" fill="{CY}" fill-opacity=".10"/>')

    # 12 chips on a 4x3 grid, wired boustrophedon so Jan→Dec is one data bus
    cols, rows = 4, 3
    cellw = (gx1 - gx0) / cols
    cellh = (gy1 - 150 - gy0) / rows
    chipw, chiph = cellw - 44, cellh - 34
    centers = []
    chips = []
    for mi, ((yr, mo), mdays) in enumerate(months):
        r, c = divmod(mi, cols)
        c = c if r % 2 == 0 else cols - 1 - c                  # snake
        cxp = gx0 + cellw * c + (cellw - chipw) / 2
        cyp = gy0 + 24 + cellh * r + (cellh - chiph) / 2
        centers.append((cxp + chipw / 2, cyp + chiph / 2, cxp, cyp, chipw, chiph))
        label = datetime.date(yr, mo, 1).strftime("%b").upper()
        msum = sum(n for _, n in mdays)
        cut = 9
        box = f"M{cxp} {cyp+cut}L{cxp+cut} {cyp}H{cxp+chipw}V{cyp+chiph}H{cxp}Z"
        chips.append(f'<path d="{box}" fill="{BG}" stroke="{CY}" stroke-opacity=".5"/>')
        chips.append(f'<circle cx="{cxp+cut+5}" cy="{cyp+cut+5}" r="2" fill="{CY}" fill-opacity=".7"/>')   # pin-1 dot
        chips.append(f'<text x="{cxp+chipw/2}" y="{cyp+chiph/2+2}" text-anchor="middle" font-weight="700" class="cy" style="font-size:16px" letter-spacing="2">{label}</text>')
        chips.append(f'<text x="{cxp+chipw/2}" y="{cyp+chiph/2+18}" text-anchor="middle" class="dim" style="font-size:10px">{msum} commits</text>')
        # day pins: split along top & bottom edges, lit by that day's level
        nd = len(mdays)
        top_n = (nd + 1) // 2
        for di, (d, n) in enumerate(mdays):
            edge_top = di < top_n
            k = di if edge_top else di - top_n
            span = top_n if edge_top else nd - top_n
            px = cxp + 10 + (chipw - 20) * (k + .5) / max(span, 1)
            py = cyp if edge_top else cyp + chiph
            if n == 0:
                col, ph = R.WIN_OFF, 4
            else:
                col, ph = pad_cols[sum(n > t for t in lv)], 7
            yoff = -ph if edge_top else 0
            chips.append(f'<rect x="{px-1.6:.1f}" y="{py+yoff:.1f}" width="3.2" height="{ph}" fill="{col}"/>')

    # route the data bus through chip gutters: out the right/left side, into the next chip
    traces, pulses = [], []
    for i in range(len(centers) - 1):
        ax, ay = centers[i][0], centers[i][1]
        bx, by = centers[i + 1][0], centers[i + 1][1]
        r_a = i // cols
        # leave from the trailing edge, run in the gutter below the row, rise into next
        ox_a = centers[i][2] + centers[i][4] if (r_a % 2 == 0) else centers[i][2]
        ox_b = centers[i + 1][2] if ((i + 1) // cols) % 2 == 0 else centers[i + 1][2] + centers[i + 1][4]
        if r_a == (i + 1) // cols:                             # same row: straight hop
            midy = ay
            d = f"M{ox_a:.1f} {ay:.1f}H{ox_b:.1f}"
        else:                                                   # drop to next row through the gutter
            guttery = centers[i][1] + centers[i][5] / 2 + (cellh - chiph) / 2 + 2
            d = (f"M{ox_a:.1f} {ay:.1f}L{ox_a+8:.1f} {ay:.1f}L{ox_a+8:.1f} {guttery:.1f}"
                 f"L{ox_b-8:.1f} {guttery:.1f}L{ox_b-8:.1f} {by:.1f}L{ox_b:.1f} {by:.1f}")
        traces.append(f'<path d="{d}" fill="none" stroke="{AM}" stroke-width="2" stroke-opacity=".75"/>')
        traces.append(f'<path d="{d}" fill="none" stroke="{AM}" stroke-width="2" stroke-opacity=".4" filter="url(#g)"/>')
        pulses.append(f'<circle r="2.4" fill="#fff"><animateMotion dur="{2.4+i*0.15:.1f}s" repeatCount="indefinite" path="{d}"/></circle>')

    # gold edge connector along the bottom
    fingers = "".join(f'<rect x="{gx0+30+i*30}" y="656" width="20" height="18" fill="{AM}" fill-opacity=".8"/>'
                      for i in range(int((gx1 - gx0 - 60) // 30)))

    side = (f'<text x="{FR-36}" y="124" text-anchor="end" class="dim" style="font-size:12px"><tspan class="cy" font-weight="700">{total:,}</tspan> commits routed · 365 days</text>'
            f'<text x="{FR-36}" y="142" text-anchor="end" class="dim" style="font-size:12px">busiest <tspan class="fg">{busiest_d:%b} {busiest_d.day}</tspan> · {busiest_n} · {active} active days</text>')
    legend = "".join(f'<rect x="{X+96+i*16}" y="642" width="11" height="11" fill="{c}"/>'
                     for i, c in enumerate([R.WIN_OFF] + pad_cols))

    body = R.heading(44, "contribution-circuit", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> fab --board 12-layer <tspan fill="#484f58"># a month per chip, a day per pin</tspan></text></g>
{side}
<rect x="{gx0}" y="{gy0}" width="{gx1-gx0}" height="{gy1-gy0}" rx="6" fill="{board}" fill-opacity=".45" stroke="{CY}" stroke-opacity=".25"/>
<g>{"".join(vias)}</g>
<g>{"".join(traces)}</g>
<g>{"".join(chips)}</g>
<g>{"".join(pulses)}</g>
{fingers}
<text x="{X}" y="652" class="dim" style="font-size:11px">unpopulated</text>{legend}<text x="{X+96+5*16+6}" y="652" class="dim" style="font-size:11px">hot pin</text>'''
    css = ""
    defs = ""
    desc = (f"Contribution board: the last year laid out as a printed circuit — twelve month-chips wired Jan→Dec into one data bus, "
            f"each day a solder pad lit by that day's activity, with a gold edge connector. "
            f"{total:,} commits, {active} active days, busiest {busiest_d:%B} {busiest_d.day} with {busiest_n}.")
    text = ("~/contribution-circuit// 02$ fab --board 12-layer # a month per chip, a day per pin"
            "commits routed 365 days busiest active days unpopulated hot pin"
            "JANFEBMARAPRMAYJUNJULAUGSEPOCTNOVDEC")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution board", desc=desc,
                       text=text, css=css, defs=defs)


# ═══════════════════════════════ 5 · terrain ══════════════════════════════════
def build_terrain(calendar, updated, as_parts=False):
    """Side-on mountain range: the year as layered, parallax hills; peaks are busy days."""
    CY, MG, GR, AM, VI, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.VIOLET, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    active = sum(1 for n in counts if n)
    busiest_i, (busiest_d, busiest_n) = max(enumerate(days), key=lambda t: t[1][1])
    N = len(days)
    rnd = R._rng(f"{updated}-{total}-terrain")
    base, amp = 596, 300

    def ridge(scale, yoff, shift):
        pts = [(FL + (FR - FL) * i / (N - 1), base + yoff - amp * scale * math.sqrt(days[(i + shift) % N][1] / peak))
               for i in range(N)]
        return pts, (f"M{FL} {base + yoff + 84}" + "".join(f"L{x:.1f} {y:.1f}" for x, y in pts) + f"L{FR} {base + yoff + 84}Z")

    _, back = ridge(.45, -98, 150)
    _, mid = ridge(.72, -50, 60)
    fpts, front = ridge(1.0, 0, 0)

    stars = "".join(f'<circle{" class=\"s0\"" if i%3==0 else ""} cx="{FL+next(rnd)*(FR-FL):.0f}" cy="{128+next(rnd)*150:.0f}" r="{(.7,1,1.3)[i%3]:.1f}" fill="#dfe8f0" opacity="{.3+next(rnd)*.5:.2f}"/>'
                    for i in range(38))
    sunx, suny = FR - 250, 184
    clouds = "".join(f'<g class="cloud{i%2}" opacity=".10"><ellipse cx="{FL+120+i*170}" cy="{168+(i%2)*38}" rx="54" ry="14" fill="{CY}"/></g>' for i in range(4))

    caps = ""
    for i in sorted(range(N), key=lambda j: -days[j][1])[:7]:
        if days[i][1]:
            x, y = fpts[i]
            caps += f'<path d="M{x-7:.1f} {y+12:.1f}L{x:.1f} {y:.1f}L{x+7:.1f} {y+12:.1f}Z" fill="{R.WIN_ON}" opacity=".9"/>'

    px, py = fpts[busiest_i]
    peak = (f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{py-36:.1f}" stroke="{AM}" stroke-width="1.6"/>'
            f'<path d="M{px:.1f} {py-36:.1f}l16 5-16 5Z" fill="{AM}"/>'
            f'<circle class="beacon" cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="{MG}" filter="url(#g)"/>'
            f'<text x="{px+22:.1f}" y="{py-32:.1f}" font-weight="800" fill="{AM}" letter-spacing="2" style="font-size:13px">SUMMIT</text>'
            f'<text x="{px+22:.1f}" y="{py-17:.1f}" class="dim" style="font-size:11px">{busiest_d:%b %-d} · {busiest_n}</text>')

    rx = FR - 36
    read = [("TOTAL", f"{total:,}"), ("SUMMIT", f"{busiest_n}"), ("ACTIVE", f"{active}/{N}d")]
    hud = "".join(f'<text x="{rx}" y="{150+i*48}" text-anchor="end" letter-spacing="1.5" class="dim" style="font-size:10px">{k}</text>'
                  f'<text x="{rx}" y="{150+i*48+22}" text-anchor="end" font-weight="800" class="wh" style="font-size:20px">{v}</text>'
                  for i, (k, v) in enumerate(read))

    body = R.heading(44, "contribution-terrain", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> survey --elevation 365d <tspan fill="#484f58"># one ridge per year, peaks are busy days</tspan></text></g>
<g>{stars}</g>
<circle cx="{sunx}" cy="{suny}" r="46" fill="url(#sunglow)"/>
<circle cx="{sunx}" cy="{suny}" r="18" fill="{AM}" opacity=".9"/>
{clouds}
<path d="{back}" fill="url(#g_back)"/>
<path d="{mid}" fill="url(#g_mid)"/>
<path d="{front}" fill="url(#g_front)"/>
<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in fpts)}" fill="none" stroke="{R.WIN_ON}" stroke-opacity=".45" stroke-width="1"/>
{caps}
{peak}
{hud}
<rect x="{FL}" y="{base+82}" width="{FR-FL}" height="2" fill="{CY}" opacity=".3" filter="url(#g)"/>'''
    css = """@keyframes tw{0%,100%{opacity:.9}50%{opacity:.15}}
@keyframes beaconb{0%,84%,100%{opacity:1}42%{opacity:.12}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(60px)}}
@keyframes drift2{from{transform:translateX(0)}to{transform:translateX(-52px)}}
.s0{animation:tw 3s infinite}.beacon{animation:beaconb 1.6s ease-in-out infinite}
.cloud0{animation:drift 22s ease-in-out infinite alternate}.cloud1{animation:drift2 27s ease-in-out infinite alternate}"""
    defs = (f'<radialGradient id="sunglow"><stop offset="0" stop-color="{AM}" stop-opacity=".5"/><stop offset="1" stop-color="{AM}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="g_back" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{R.ROOFS[1]}" stop-opacity=".55"/><stop offset="1" stop-color="{BG}" stop-opacity=".15"/></linearGradient>'
            f'<linearGradient id="g_mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{R.ROOFS[2]}" stop-opacity=".8"/><stop offset="1" stop-color="{R.FACE_R}"/></linearGradient>'
            f'<linearGradient id="g_front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{R.ROOFS[3]}"/><stop offset=".5" stop-color="{R.FACE_L}"/><stop offset="1" stop-color="{BG}"/></linearGradient>')
    desc = (f"Contribution terrain: the last year as a layered mountain range, taller peaks for busier days. "
            f"{total:,} contributions, highest summit {busiest_d:%B} {busiest_d.day} with {busiest_n}, {active} active days.")
    text = ("~/contribution-terrain// 02$ survey --elevation 365d # one ridge per year, peaks are busy days"
            "SUMMIT TOTAL ACTIVE JanFebMarAprMayJunJulAugSepOctNovDec")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution terrain", desc=desc, text=text, css=css, defs=defs)


# ═══════════════════════════════ 6 · rally ════════════════════════════════════
def build_rally(calendar, updated, as_parts=False):
    """A rally stage: the year's profile is the road; a car drives its climbs and drops,
    the surface (gravel / tarmac / snow) coloured by how busy each day was."""
    CY, MG, GR, AM, VI, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.VIOLET, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    lv = R._levels(counts)
    active = sum(1 for n in counts if n)
    busiest_i, (busiest_d, busiest_n) = max(enumerate(days), key=lambda t: t[1][1])
    N = len(days)
    base, amp, W0, W1 = 538, 300, FL + 8, FR - 8
    pts = [(W0 + (W1 - W0) * i / (N - 1), base - amp * math.sqrt(n / peak)) for i, (d, n) in enumerate(days)]
    road_d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    fill_d = f"M{W0} {base+124}" + "".join(f"L{x:.1f} {y:.1f}" for x, y in pts) + f"L{W1} {base+124}Z"
    surf = {0: AM, 1: AM, 2: "#2a3340", 3: R.WIN_ON}
    segs = []
    for i in range(N - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        lvl = sum(days[i][1] > t for t in lv) if days[i][1] else 0
        segs.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{surf[lvl]}" stroke-width="5" stroke-linecap="round"/>')
    centerline = f'<path d="{road_d}" fill="none" stroke="{BG}" stroke-width="1" stroke-dasharray="6 8" opacity=".5"/>'
    car = (f'<g><g transform="translate(-9 -7)">'
           f'<path d="M0 8L3 2H13L18 6V10H0Z" fill="{MG}"/><rect x="4" y="0" width="7" height="4" fill="{CY}"/>'
           f'<circle cx="4.5" cy="11" r="2.4" fill="#0b0d12"/><circle cx="14.5" cy="11" r="2.4" fill="#0b0d12"/></g>'
           f'<animateMotion dur="15s" repeatCount="indefinite" rotate="auto" path="{road_d}"/></g>')
    fx = W1
    finish = (f'<rect x="{fx-4:.0f}" y="{base-amp-14:.0f}" width="4" height="{amp+138:.0f}" fill="#6e7681" opacity=".45"/>'
              + "".join(f'<rect x="{fx-4:.0f}" y="{base-amp-14+j*8:.0f}" width="4" height="4" fill="{"#f0f6fc" if j%2 else "#0b0d12"}"/>' for j in range(7)))
    px, py = pts[busiest_i]
    peak = (f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{py-30:.1f}" stroke="{AM}" stroke-width="1.4"/><path d="M{px:.1f} {py-30:.1f}l15 5-15 5Z" fill="{AM}"/>'
            f'<text x="{px+20:.1f}" y="{py-26:.1f}" font-weight="800" fill="{AM}" letter-spacing="1" style="font-size:12px">KING STAGE</text>'
            f'<text x="{px+20:.1f}" y="{py-12:.1f}" class="dim" style="font-size:11px">{busiest_d:%b %-d} · {busiest_n}</text>')
    rx = FR - 36
    read = [("STAGE", "365d"), ("FASTEST", f"{busiest_n}"), ("DRIVEN", f"{active}d")]
    hud = "".join(f'<text x="{rx}" y="{150+i*46}" text-anchor="end" letter-spacing="1.5" class="dim" style="font-size:10px">{k}</text>'
                  f'<text x="{rx}" y="{150+i*46+21}" text-anchor="end" font-weight="800" class="wh" style="font-size:19px">{v}</text>'
                  for i, (k, v) in enumerate(read))
    leg = (f'<rect x="{X}" y="628" width="11" height="11" fill="{AM}"/><text x="{X+16}" y="638" class="dim" style="font-size:11px">gravel</text>'
           f'<rect x="{X+92}" y="628" width="11" height="11" fill="#2a3340"/><text x="{X+108}" y="638" class="dim" style="font-size:11px">tarmac</text>'
           f'<rect x="{X+186}" y="628" width="11" height="11" fill="{R.WIN_ON}"/><text x="{X+202}" y="638" class="dim" style="font-size:11px">snow</text>')
    body = R.heading(44, "contribution-rally", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> rally --stage WRC <tspan fill="#484f58"># drive the year, surface = intensity</tspan></text></g>
<path d="{fill_d}" fill="url(#g_rally)"/>
{"".join(segs)}
{centerline}
{finish}
{peak}
{car}
{hud}
{leg}'''
    css = "@keyframes beaconb{0%,84%,100%{opacity:1}42%{opacity:.12}}"
    defs = f'<linearGradient id="g_rally" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{R.FACE_R}" stop-opacity=".7"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
    desc = (f"Contribution rally: the year's activity profile as a rally stage road a car drives, surfaces coloured by intensity "
            f"(gravel, tarmac, snow). {total:,} contributions, fastest split {busiest_d:%B} {busiest_d.day} with {busiest_n}.")
    text = ("~/contribution-rally// 02$ rally --stage WRC # drive the year, surface = intensity"
            "STAGE FASTEST DRIVEN KING gravel tarmac snow JanFebMarAprMayJunJulAugSepOctNovDec")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution rally", desc=desc, text=text, css=css, defs=defs)


# ═══════════════════════════════ 7 · pulse ════════════════════════════════════
def build_pulse(calendar, updated, as_parts=False):
    """A vitals monitor: the year as an ECG trace — a spike per busy day, a beat sweeping across."""
    CY, MG, GR, AM, VI, BG = R.CYAN, R.MAGENTA, R.GREEN, R.AMBER, R.VIOLET, R.BG
    FL, FR, X = R.FL, R.FR, R.X
    days = _days(calendar)
    counts = [n for _, n in days]
    total, peak = sum(counts), max(counts) if counts else 1
    active = sum(1 for n in counts if n)
    busiest_i, (busiest_d, busiest_n) = max(enumerate(days), key=lambda t: t[1][1])
    N = len(days)
    W0, W1, cen, amp = FL + 36, FR - 150, 414, 176
    P = [(W0, cen)]
    for i, (d, n) in enumerate(days):
        x = W0 + (W1 - W0) * i / (N - 1)
        if not n:
            P.append((x, cen))
        else:
            h = amp * math.sqrt(n / peak)
            P += [(x - 2, cen), (x - 0.8, cen + h * 0.16), (x, cen - h), (x + 0.9, cen + h * 0.3), (x + 2, cen)]
    P.append((W1, cen))
    trace = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in P)
    grid = "".join(f'<line x1="{gx}" y1="150" x2="{gx}" y2="602" stroke="{GR}" stroke-opacity=".06"/>' for gx in range(int(W0), int(W1), 26))
    grid += "".join(f'<line x1="{W0}" y1="{gy}" x2="{W1}" y2="{gy}" stroke="{GR}" stroke-opacity=".06"/>' for gy in range(166, 602, 26))
    beat = f'<circle r="4.2" fill="#eafff2" filter="url(#g)"><animateMotion dur="9s" repeatCount="indefinite" path="{trace}"/></circle>'
    sweep = f'<line class="scan" x1="{W0}" y1="156" x2="{W0}" y2="600" stroke="{GR}" stroke-opacity=".5" stroke-width="2" filter="url(#g)"/>'
    px, py = W0 + (W1 - W0) * busiest_i / (N - 1), cen - amp * math.sqrt(busiest_n / peak)
    peak = (f'<circle class="beacon" cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{AM}" filter="url(#g)"/>'
            f'<text x="{px:.1f}" y="{py-10:.1f}" text-anchor="middle" font-weight="800" fill="{AM}" letter-spacing="1" style="font-size:12px">PEAK</text>'
            f'<text x="{px:.1f}" y="{py-24:.1f}" text-anchor="middle" class="dim" style="font-size:10px">{busiest_d:%b %-d} · {busiest_n}</text>')
    heart = (f'<g class="hb" style="transform-origin:{W0+10}px 118px"><path transform="translate({W0} 108) scale(1.4)" d="{R.HEART}" fill="{MG}"/></g>'
             f'<text x="{W0+34}" y="122" class="gr" font-weight="700" style="font-size:15px">{active}</text>'
             f'<text x="{W0+34}" y="122" class="dim" style="font-size:15px" dx="{len(str(active))*9+4}"> active beats / 365</text>')
    rx = FR - 36
    read = [("PEAK/DAY", f"{busiest_n}"), ("ACTIVE", f"{active}d"), ("TOTAL", f"{total:,}")]
    hud = "".join(f'<text x="{rx}" y="{172+i*50}" text-anchor="end" letter-spacing="1.5" class="dim" style="font-size:10px">{k}</text>'
                  f'<text x="{rx}" y="{172+i*50+23}" text-anchor="end" font-weight="800" class="gr" style="font-size:21px">{v}</text>'
                  for i, (k, v) in enumerate(read))
    body = R.heading(44, "contribution-pulse", "// 02") + f'''
<g class="ln" style="animation-delay:.15s"><text x="{X}" y="96" class="dim"><tspan class="gr">$</tspan> vitals --ecg 365d <tspan fill="#484f58"># one beat per day, spikes are busy days</tspan></text></g>
<g>{grid}</g>
{heart}
<path d="{trace}" fill="none" stroke="{GR}" stroke-opacity=".3" stroke-width="2"/>
<path d="{trace}" fill="none" stroke="{GR}" stroke-width="2" filter="url(#g)" opacity=".6"/>
<path d="{trace}" fill="none" stroke="{R.WIN_ON if False else GR}" stroke-width="1.6"/>
{sweep}
{peak}
{beat}
{hud}'''
    css = """@keyframes scan{from{transform:translateX(0)}to{transform:translateX(""" + f"{W1-W0:.0f}" + """px)}}
@keyframes hb{0%,100%{transform:scale(1)}15%{transform:scale(1.22)}30%{transform:scale(1)}}
@keyframes beaconb{0%,84%,100%{opacity:1}42%{opacity:.12}}
.scan{animation:scan 9s linear infinite}.hb{animation:hb 1.3s ease-in-out infinite}.beacon{animation:beaconb 1.6s ease-in-out infinite}"""
    defs = ""
    desc = (f"Contribution pulse: the last year as an ECG vitals trace, a tall spike for each busy day and a beat sweeping across. "
            f"{total:,} contributions, {active} active days, strongest beat {busiest_d:%B} {busiest_d.day} with {busiest_n}.")
    text = ("~/contribution-pulse// 02$ vitals --ecg 365d # one beat per day, spikes are busy days"
            "PEAK/DAY ACTIVE TOTAL active beats / 365 JanFebMarAprMayJunJulAugSepOctNovDec")
    if as_parts:
        return body, css, defs, text
    return R.slice_svg(680, body, title="Contribution pulse", desc=desc, text=text, css=css, defs=defs)


# ═══════════════════════════ cycle (all views in one) ═════════════════════════
def build_cycle(calendar, updated):
    """All six views in one slice, cross-fading in turn; the heading swaps with each.

    Every view's body is stacked in its own group and only the group opacity animates,
    so each view keeps its own animations running underneath. Class/keyframe names that
    overlap between views are near-identical (the city's window code is reused), so a
    plain concat is safe; the only id clash is the shared moon gradient (first wins).
    """
    views = [("cycA", build_reactor), ("cycB", build_terrain), ("cycC", build_rally),
             ("cycD", build_pulse), ("cycE", build_circuit), ("cycF", build_metropolis), ("cycG", R.build_city)]
    groups, csss, defss, texts = [], [], [], []
    for cls, fn in views:
        b, c, d, t = fn(calendar, updated, as_parts=True)
        groups.append(f'<g class="cyc {cls}">{b}</g>')
        csss.append(c)
        defss.append(d)
        texts.append(t)
    cyc_css = """@keyframes cycA{0%{opacity:1}14%{opacity:1}16%{opacity:0}98%{opacity:0}100%{opacity:1}}
@keyframes cycB{0%{opacity:0}12%{opacity:0}14%{opacity:1}29%{opacity:1}31%{opacity:0}100%{opacity:0}}
@keyframes cycC{0%{opacity:0}27%{opacity:0}29%{opacity:1}43%{opacity:1}45%{opacity:0}100%{opacity:0}}
@keyframes cycD{0%{opacity:0}41%{opacity:0}43%{opacity:1}57%{opacity:1}59%{opacity:0}100%{opacity:0}}
@keyframes cycE{0%{opacity:0}55%{opacity:0}57%{opacity:1}71%{opacity:1}73%{opacity:0}100%{opacity:0}}
@keyframes cycF{0%{opacity:0}69%{opacity:0}71%{opacity:1}86%{opacity:1}88%{opacity:0}100%{opacity:0}}
@keyframes cycG{0%{opacity:0}84%{opacity:0}86%{opacity:1}100%{opacity:1}}
.cyc{animation-duration:70s;animation-iteration-count:infinite;animation-timing-function:ease-in-out;opacity:0}
.cycA{animation-name:cycA;opacity:1}.cycB{animation-name:cycB}.cycC{animation-name:cycC}.cycD{animation-name:cycD}.cycE{animation-name:cycE}.cycF{animation-name:cycF}.cycG{animation-name:cycG}"""
    total = sum(n for _, n in calendar)
    return R.slice_svg(680, "".join(groups), title="Contribution — cycling views",
                       desc=("Contribution activity for the last year, cycling between a reactor, a mountain terrain, a rally stage, "
                             f"an ECG pulse, a circuit board, a neon metropolis and an isometric city. {total:,} contributions."),
                       text="".join(texts), css="\n".join(csss + [cyc_css]), defs="".join(defss))


BUILDERS = {"reactor": build_reactor, "metropolis": build_metropolis, "circuit": build_circuit,
            "terrain": build_terrain, "rally": build_rally, "pulse": build_pulse, "cycle": build_cycle}


if __name__ == "__main__":  # smoke test: every variant renders against the real data
    import pathlib
    H = pathlib.Path(__file__).resolve().parent
    R.apply_theme(json.load(open(H / "themes.json"))["cyberpunk"])
    cal = json.load(open(H / "data" / "calendar.json"))
    upd = json.load(open(H / "data" / "stats.json"))["updated"]
    for nm, fn in BUILDERS.items():
        svg = fn(cal, upd)
        assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>"), nm
    assert "PEAK" in build_reactor(cal, upd) and "PEAK" in build_metropolis(cal, upd), "peak not highlighted"
    print("city_variants: all variants render; peak highlighted ✓")
