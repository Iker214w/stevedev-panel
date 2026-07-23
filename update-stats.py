#!/usr/bin/env python3
"""Genera stats.json con los datos públicos del canal SteveDev (para GitHub Actions)."""
import json, subprocess, sys, datetime, os

CANAL = "https://www.youtube.com/@Steve_developer-real/shorts"
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")

def ytdlp(*args):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", *args], capture_output=True, text=True, timeout=420)
    return r.stdout.strip()

def n(v):
    return None if v in ("NA", "", None) else int(v)

try:
    ids = []
    for line in ytdlp("--flat-playlist", "--print", "%(id)s", CANAL).splitlines():
        line = line.strip()
        if line and line not in ids:
            ids.append(line)
    if not ids:
        raise RuntimeError("lista de vídeos vacía (¿YouTube bloqueó al runner?)")

    subs = n(ytdlp("--flat-playlist", "--playlist-items", "1",
                   "--print", "%(channel_follower_count)s", CANAL).splitlines()[0].strip() if ids else "NA")

    vids = []
    for vid in ids:
        out = ytdlp("--skip-download", "--print",
                    "%(id)s|%(title)s|%(view_count)s|%(like_count)s|%(comment_count)s|%(upload_date)s|%(duration)s",
                    f"https://youtube.com/shorts/{vid}")
        if not out:
            continue
        i, t, v, l, c, d, du = out.split("|")
        vids.append(dict(id=i, titulo=t, vistas=n(v) or 0, likes=n(l), coms=n(c),
                         fecha=f"{d[6:8]}/{d[4:6]}/{d[0:4]}", dur=(n(du) or 0),
                         thumb=f"https://i.ytimg.com/vi/{i}/hqdefault.jpg"))
    if not vids:
        raise RuntimeError("sin métricas de ningún vídeo")

    json.dump({"actualizado": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "subs": subs, "videos": vids},
              open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK · {len(vids)} vídeos · {sum(v['vistas'] for v in vids)} vistas")
except Exception as e:
    # ante cualquier fallo, conservar el stats.json anterior (no romper el panel)
    print(f"AVISO: {e} — se conserva el stats.json previo", file=sys.stderr)
    sys.exit(0)
