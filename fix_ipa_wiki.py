# -*- coding: utf-8 -*-
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(r"C:\Users\admin\Desktop\书籍\英语语法\englishism")
IPA = BASE / "audio" / "ipa"
MD = BASE / "MinerU_markdown_谢孟媛英语教学《发音篇》课程讲义_2066808178470641664.md"
GH = "https://cdn.jsdelivr.net/gh/joshstephenson/PhoneticFlashCards@main/ipa_audio"

DOWNLOADS = {
    "i.mp3": "vowels/Close_front_unrounded_vowel_i.ogg.mp3",
    "ih.mp3": "vowels/Near-close_near-front_unrounded_vowel_ɪ.ogg.mp3",
    "eh.mp3": "vowels/Close-mid_front_unrounded_vowel_e.ogg.mp3",
    "epsilon.mp3": "vowels/Open-mid_front_unrounded_vowel_ɛ.ogg.mp3",
    "ae.mp3": "vowels/Near-open_front_unrounded_vowel_æ.ogg.mp3",
    "schwa.mp3": "vowels/Mid-central_vowel_ə.ogg.mp3",
    "u.mp3": "vowels/Close_back_rounded_vowel_u.ogg.mp3",
    "ush.mp3": "vowels/Near-close_near-back_rounded_vowel_ʊ.ogg.mp3",
    "aw.mp3": "vowels/Open-mid_back_rounded_vowel_ɔ.ogg.mp3",
    "ah.mp3": "vowels/Open_back_unrounded_vowel_ɑ.ogg.mp3",
    "er.mp3": "vowels/Open-mid_central_unrounded_vowel_ɜ.ogg.mp3",
    "a.mp3": "vowels/Open_front_unrounded_vowel_a.ogg.mp3",
    "o_mono.mp3": "vowels/Close_mid_back_rounded_vowel_o.ogg.mp3",
    "p.mp3": "consonants/archive/Voiceless_bilabial_plosive.ogg.mp3",
    "b.mp3": "consonants/archive/Voiced_bilabial_plosive.ogg.mp3",
    "t.mp3": "consonants/Voiceless_alveolar_plosive_t.ogg.mp3",
    "d.mp3": "consonants/Voiced_alveolar_plosive_d.ogg.mp3",
    "k.mp3": "consonants/Voiceless_velar_plosive_k.ogg.mp3",
    "g.mp3": "consonants/Voiced_velar_plosive_g.ogg.mp3",
    "f.mp3": "consonants/Voiceless_labio-dental_fricative_f.ogg.mp3",
    "v.mp3": "consonants/Voiced_labio-dental_fricative_v.ogg.mp3",
    "s.mp3": "consonants/Voiceless_alveolar_sibilant_s.ogg.mp3",
    "z.mp3": "consonants/Voiced_alveolar_sibilant_z.ogg.mp3",
    "th.mp3": "consonants/Voiceless_dental_fricative_θ.ogg.mp3",
    "dh.mp3": "consonants/Voiced_dental_fricative_ð.ogg.mp3",
    "sh.mp3": "consonants/Voiceless_palato-alveolar_sibilant_ʃ.ogg.mp3",
    "zh.mp3": "consonants/Voiced_palato-alveolar_sibilant_ʒ.ogg.mp3",
    "ch.mp3": "consonants/archive/Voiceless_palato-alveolar_affricate.ogg.mp3",
    "jh.mp3": "consonants/archive/Voiced_palato-alveolar_affricate.ogg.mp3",
    "h.mp3": "consonants/archive/Voiceless_glottal_fricative.ogg.mp3",
    "m.mp3": "consonants/Bilabial_nasal_m.ogg.mp3",
    "n.mp3": "consonants/Alveolar_nasal_n.ogg.mp3",
    "ng.mp3": "consonants/Velar_nasal_ŋ.ogg.mp3",
    "l.mp3": "consonants/Voiced_alveolar_lateral_approximant_l.ogg.mp3",
    "r.mp3": "consonants/archive/Alveolar_approximant_ɹ.ogg.mp3",
    "w.mp3": "consonants/archive/Voiced_labio-velar_approximant.ogg.mp3",
    "y.mp3": "consonants/Voiced_palatal_approximant_j.ogg.mp3",
}

CONCAT = {
    "ey.mp3": ("eh.mp3", "ih.mp3"),
    "ai.mp3": ("a.mp3", "ih.mp3"),
    "au.mp3": ("a.mp3", "u.mp3"),
    "oi.mp3": ("aw.mp3", "ih.mp3"),
    "oh.mp3": ("o_mono.mp3", "ush.mp3"),
    "er_r.mp3": ("schwa.mp3", "r.mp3"),
}

JUNK = ("x.mp3", "d3.mp3", "j.mp3", "o.mp3", "e_mono.mp3", "e.mp3")


def gh_url(rel: str) -> str:
    return GH + "/" + "/".join(urllib.parse.quote(p) for p in rel.split("/"))


def download(rel: str, dest: Path):
    url = gh_url(rel)
    last = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) < 1000:
                raise RuntimeError("too small")
            dest.write_bytes(data)
            return
        except Exception as e:
            last = e
            time.sleep(1)
    raise last


def concat_mp3(out: Path, parts: list[Path]):
    with open(out, "wb") as o:
        for p in parts:
            o.write(p.read_bytes())


def fix_md(text: str) -> str:
    text = text.replace('src="audio/ipa/I.mp3"', 'src="audio/ipa/ih.mp3"')
    text = text.replace('src="audio/ipa/U.mp3"', 'src="audio/ipa/ush.mp3"')
    text = text.replace(
        'src="audio/ipa/e.mp3"></audio> **[ e ]**',
        'src="audio/ipa/ey.mp3"></audio> **[ e ]**',
    )
    text = text.replace(
        'src="audio/ipa/e.mp3"></audio> **【e】**',
        'src="audio/ipa/eh.mp3"></audio> **【e】**',
    )
    text = text.replace("src=\"audio/beat.mp3\"></audio> **【i】**", 'src="audio/ipa/i.mp3"></audio> **【i】**')
    text = text.replace("src=\"audio/bit.mp3\"></audio> **【I】**", 'src="audio/ipa/ih.mp3"></audio> **【I】**')
    text = text.replace("src=\"audio/bait.mp3\"></audio> **【e】**", 'src="audio/ipa/ey.mp3"></audio> **【e】**')
    note = "> 音标：标准 KK/IPA 单音（Wikipedia）；双元音为合成；单词/例句为完整读音"
    for old in (
        "> 音标：谢孟媛《全音标》视频原声切割；单词/例句为完整读音",
        "> 音标：Wikipedia IPA 单音（ih/ush 区分 ɪ/ʊ）；双元音 ey/ai/au/oi/oh 为合成；单词/例句为完整读音",
        "> 音标：Wikipedia IPA 单音；单词/例句：完整读音",
    ):
        text = text.replace(old, note)
    return text


def main():
    IPA.mkdir(parents=True, exist_ok=True)
    for fname, rel in DOWNLOADS.items():
        download(rel, IPA / fname)
        print("ok", fname)

    shutil.copy2(IPA / "schwa.mp3", IPA / "uh.mp3")
    print("ok uh.mp3")

    for out, parts in CONCAT.items():
        concat_mp3(IPA / out, [IPA / p for p in parts])
        print("concat", out)

    for name in JUNK:
        (IPA / name).unlink(missing_ok=True)

    text = MD.read_text(encoding="utf-8")
    MD.write_text(fix_md(text), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
