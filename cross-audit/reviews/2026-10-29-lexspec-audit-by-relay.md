# Входящий аудит: lexspec, 2026-10-29

Источник: mak777uh/-, cross-audit/outgoing/2026-10-29-lexspec-audit.md. Копия дословная, без правок;
разбор находок — в [docs/30](../../docs/30-REPO-WALK.md) §11 и §12.

---

<!-- Крестовый аудит: внешнее мнение, не приговор.
     Автор: ведущий научной лаборатории (агент deepseek), дата 2026-10-29.
     Все находки проверены чтением файлов и, где указано, прогонами; файлы репозитория при аудите не менялись.
     Репозиторий: mak777uh/lexspec — спецификация, схема и чекер юридических утверждений (позиции Хофельда, привязка к спану)
     Прочитать за 30 секунд: раздел «Пять пунктов» в конце.
-->

# Внешний аудит: lexspec (v0.1)

Объект: `_cross_audit/lexspec`, коммит `a2c1552` (единственный в истории), ветка `main`.
Среда аудита: Windows, Python 3.13.11, `locale.getpreferredencoding() == cp1251`; в CI заявлен Python 3.11 / ubuntu-latest.
Дата: 2026-10-29. Рабочее дерево было чистым (`git status --short` — пусто), файлы репозитория не изменялись; все мутации делались в копиях под `%TEMP%\lexaudit`.

## Что проверено и как

1. **Состав и пиннинг.** `Get-ChildItem -Recurse -File` + `git log --oneline`: в `corpus/` ровно 4 `.txt` и **ни одного манифеста**; пин существует только как `corpus[].text_sha256` внутри 12 утверждений. Хеши всех четырёх файлов снял `Get-FileHash -Algorithm SHA256` и сверил с объявлениями: совпадают (шесть утверждений, `examples/01`–`06`, ссылаются на один и тот же `gk-rf-2026-10-01.txt` с одним хешем `5fee7dad…`).
2. **Прогон чекера и статуса.** `python tools/lexcheck.py examples/*.lex.json` — 12 отчётов, exit 1 (3 REFUSED); `python tools/lexspec_status.py` — `examples: 12`, `atoms: 52 total, 38 closed (73.1%), 51 anchored (98.1%)`, `corpus: 4 pinned file(s), digests match declarations: yes`.
3. **Гейты.** `python tests/run_tests.py` — `Ran 74 tests in 41.192s / OK`. Список тестов выгружен и просмотрен по именам (негативные случаи есть, см. ниже).
4. **Схема против примеров.** Валидировал все 12 примеров `jsonschema` Draft202012 против `schemas/statement-0.1.json`: 3 падения, все на `quantities[0].period.segments`.
5. **Мутационные проверки** (копии в `%TEMP%`, запуск с `--root <repo>`): `revision: 2026-10-28 → 1999-01-01`; `anchor.article: "ст. 395 п. 1" → "ст. 999 п. 42"`; span с переводом строки и утроенным пробелом; удаление всего блока `series[0].basis`.
6. **Детерминизм.** Один и тот же файл при `PYTHONHASHSEED=0 / 12345 / 999` и из двух разных cwd — `--json` байт-в-байт; два последовательных прогона `examples/12` — идентичны (6993 байта). `findings.ordered` имеет явный ключ `(check, atom_index, _seq)` (`tools/lexcheck.py:427-438`), `set` при формировании отчёта не итерируется.
7. **Вывод и кодировка.** `PYTHONIOENCODING=cp1252 python tools/lexcheck.py … --json > out.json` (дефолт перенаправленного stdout на en-US Windows): stdout 0 байт, traceback в stderr, exit 1.
8. **Сверка прозы с кодом.** Прочитаны `README.md`, `AGENTS.md`, `docs/10-SPEC-v0.1.md` §4-§8, `docs/11-REFUSAL-CODES.md` (фрагмент), `tools/SELFTEST.md` (фрагменты), `tools/lexspec_status.py`, `tools/check_examples.py`, `tools/selftest.py` (фрагменты), `.gitattributes`, `lab/2026-10-28-checkout-line-endings.md`, `tests/expected.json`.

## Находки

### Сломает результат

**1. Три из двенадцати поставляемых примеров не проходят опубликованную схему, и CI этого не видит.**
`examples/10-gk-rf-395-quantified.lex.json:254`, `examples/11-gk-rf-395-defeat.lex.json:255`, `examples/12-gk-rf-395-doctrinal.lex.json:364` задают `quantities[0].period.segments = "rate_change_and_payments"`, а `schemas/statement-0.1.json:542-548` допускает только `rate_change | none | undeclared`. Валидатор `jsonschema` даёт ровно эти три ошибки и больше ничего: остальные 9 примеров проходят. `lexcheck` поле `segments` не читает вообще — в `check_quantities` используются только `day_count` и `rounding` (`tools/lexcheck.py:1326`, `:1337-1339`). Ни один шаг `.github/workflows/guards.yml` не валидирует примеры схемой, а `tools/selftest.py:191-195` прямо фиксирует, что «The JSON Schema is documentation; `lexcheck.py` is the executable contract», и `run_tests.py` сверяет только required-поля и enum'ы, но не значения в примерах. Итог: опубликованный контракт и поставляемые данные расходятся, оба зелёные.

**2. Основание числового ряда не якорится ничем; поставляемый пример это уже демонстрирует.**
`examples/10-gk-rf-395-quantified.lex.json:232-233`: `series[0].basis = {corpus: "gk-rf-395", article: "Пленум ВС РФ № 7 п. 39", span: "размер процентов за пользование чужими денежными средствами"}`. Этой строки нет в `corpus/gk-rf-395-2026-10-28.txt` (проверено `"…".Contains(...)` и регистронезависимо — False; в корпусе есть только «проценты за пользование чужими средствами»), а документа «Пленум ВС РФ № 7» в корпусе нет в принципе. `_series_paths` (`tools/lexcheck.py:1151-1181`) проверяет только `id`, `path`, `digest`; `basis` не читается ни разу. Атом `a2` (`examples/10…:108`, `"quantity": "q1"`) в отчёте **закрыт**: `coverage 0.667 … 4/6 closed, 6/6 anchored`, вердикт `CHECKED`. Если удалить `basis` целиком (он обязателен по `schemas/statement-0.1.json:438-446`), отчёт не меняется: тот же `CHECKED`, `4/6 closed, 6/6 anchored`. То есть «каждое число прослеживается до спана» для L5-слоя не выполняется, и отчёт об этом молчит.

**3. `--json` падает на не-UTF-8 stdout, а код выхода 1 неотличим от честного REFUSED.**
`tools/lexcheck.py:1818` печатает `json.dumps(payload, ensure_ascii=False)`. При `PYTHONIOENCODING=cp1252` (дефолт перенаправленного stdout на англоязычной Windows) — `UnicodeEncodeError`, stdout 0 байт, traceback в stderr, `exit=1`. Ровно тот же код возврата, что у REFUSED (`README.md:52`), и stderr никто не обязан читать; в конвейере «упал» и «отказал» неразличимы. Человеческий вывод падает так же, как только в `detail` появляется кириллица: `PYTHONIOENCODING=cp1252 python tools/lexcheck.py examples/02-opposite-conflict.lex.json > out.txt` даёт `stdout 0 байт`, `UnicodeEncodeError: 'charmap' codec can't encode characters in position 439-447` и `exit=1`. `tools/check_examples.py:32-54` запускает чекер именно через pipe и при пустом stdout молча получает `report=None`.

### Сломает доверие

**4. «Закреплённая редакция» — это строка в утверждении, которую никто не сверяет.**
`revision` (`schemas/statement-0.1.json:138-143`) проверяется только на формат календарной даты (`tools/lexcheck.py:576-580`) — ни с шапкой `# REVISION:` файла, ни с датой в имени файла, ни с чем-либо ещё. Мутация копии `examples/08`: `"revision": "2026-10-28" → "1999-01-01"` и `"article": "ст. 395 п. 1" → "ст. 999 п. 42"` — вердикт не изменился (`CHECKED`, `3/6 closed, 6/6 anchored`), ни одного finding. При этом шапка самого файла говорит, что текст — «в редакции ФЗ от 03.07.2016 N 315-ФЗ и от 08.03.2015 N 42-ФЗ» (`corpus/gk-rf-395-2026-10-28.txt:2`), то есть «2026-10-28» — дата скачивания, а не редакция нормы; различить это в отчёте нельзя, потому что в отчёте нет ни id корпуса, ни его хеша, ни `revision` (полный набор ключей — `tools/lexcheck.py:1667-1687`). JSON-отчёт сам по себе не отвечает на вопрос «против каких байт и какой редакции проверено», хотя README:10-11 определяет вердикт как вердикт над тройкой.

**5. `prefix`/`suffix` объявлены частью якоря в спеке, выпускаются `span_hint.py` и полностью игнорируются чекером.**
`docs/10-SPEC-v0.1.md:230` определяет якорь как `span` **вместе с** `anchor.prefix`/`anchor.suffix`, а `docs/10-SPEC-v0.1.md:240-241` требует 32-символьный контекст, когда нормализованный span короче 40 символов. В `schemas/statement-0.1.json` этих полей нет; `check_anchors` (`tools/lexcheck.py:939-993`) читает только `corpus` и `span`. При этом `tools/span_hint.py:13`, `:115-117`, `:149-162` именно вычисляет и печатает `prefix`/`suffix` (по умолчанию 30 символов, `span_hint.py:180`, — в спеке 32), то есть рабочий процесс их производит, а вердикт от них не зависит. Проверено: подстановка в копию `examples/08` заведомо ложных `"prefix": "ЭТОГО ТЕКСТА В КОРПУСЕ НЕТ"`, `"suffix": "И ЭТОГО ТОЖЕ НЕТ"` не меняет ничего — `6/6 anchored`, `CHECKED`. В самих примерах span'ы a1=39 и a3=31 символа (`examples/08`, `examples/12`) — короче 40 и без контекста, и отчёт всё равно печатает `6/6 anchored`. Правило «context required <40» не реализовано ни в чекере, ни в тестах (в `tests/run_tests.py` нет ни одного упоминания `prefix`). Бонус: нормализация существует в двух копиях — `tools/lexcheck.py:914-925` и `tools/span_hint.py:42-45`, — и `span_hint.py:26-27` сам признаёт, что это «a second copy of the same rule», которую «the checker can import later»; пока копии совпадают, но ничто это не проверяет.

**6. `S2_HASH_MISMATCH` выдаётся там, где хеш совпал.**
`tools/lexcheck.py:900-908`: файл успешно хешируется, но не декодируется как UTF-8 → `findings.add("S2_HASH_MISMATCH", …)`. По `docs/11-REFUSAL-CODES.md:39` этот код значит «sha256 файла ≠ объявленный `text_sha256`» — здесь верно обратное (хеш равен, дело в кодировке). Вторая ветка, `tools/lexcheck.py:882-889`: `OSError` при чтении → тоже `S2_HASH_MISMATCH`, хотя собственный `detail` говорит «the declared sha256 cannot be verified». Это ровно тот дефект, который в репозитории назван F-3-1 и исправлен для отсутствующего файла (`tools/lexcheck.py:869-879`), но выжил в двух соседних ветках. Эффект: автор идёт перепинивать корпус, хотя проблема в кодировке или правах доступа.

**7. `not_claimed` — три фиксированные строки, и в них нет самого важного.**
`tools/lexcheck.py:194-198`; печатается в человеческом выводе (`:1722`) и в JSON (`:1686`). В списке нет: (а) того, что `anchor.article` не проверяется (`docs/10-SPEC-v0.1.md:263`); (б) что `revision` не проверяется; (в) что `conditions` — проза и не интерпретируется (`docs/10-SPEC-v0.1.md:188-190`); (г) что кросс-кортежная коррелятивность не проверяется (признано в docstring `tools/lexcheck.py:22-29` и только в `tools/SELFTEST.md`); (д) что нормализационная политика не объявлена в утверждении и не напечатана в отчёте, хотя `docs/10-SPEC-v0.1.md:220-222` требует и первого, и второго («declared by the statement and printed in the report»). Читатель одного JSON-отчёта без README не узнает, что «статья» в якоре — декорация.

**8. Опубликованный канонический вид и хеш корпуса в `SELFTEST.md` устарели в четырёх местах.**
`tools/SELFTEST.md:80`, `:180`, `:215`, `:245` печатают `statement_sha256 8d4f7430…` и внутри канонического вида `"text_sha256":"fc6f39a0…f36d"`. Сегодня `python tools/lexcheck.py examples/01-delivery-ok.lex.json --canonical` даёт `sha256 00f179ed760bdfa70e2c29c630dd5fda3e5609d0ff5e9bc35b30866901db9486` и `"text_sha256":"5fee7dad…12cb0"`; реальный хеш `corpus/gk-rf-2026-10-01.txt` — `5fee7dadad023cceb9f94247f76a42931dedf95c3977f04654ab758d47612cb0`. `README.md:148-149` называет этот файл «the commands and their real output». Скопировавший блок из SELFTEST получит документ, который чекер отвергнет по `S2_HASH_MISMATCH`. Дрейф невидим, потому что генератор `tools/selftest.py` в `guards.yml` не запускается ни одним шагом, а `run_tests.py`/`check_examples.py` сверяют только `tests/expected.json`.

**9. Схема обещает «exact substring», чекер матчит после нормализации — это разные контракты.**
`schemas/statement-0.1.json:289-292`: span — «Exact substring of the pinned text, occurring exactly once». `tools/lexcheck.py:914-925` перед поиском делает `html.unescape`, вырезает `<…>` и сворачивает все пробелы; `:973-975` ищет по нормализованному тексту. Проверено: замена span в копии `examples/08` на `"подлежат\nуплате   проценты на сумму долга"` (в файле — одна строка с одним пробелом) сохраняет `6/6 anchored` и вердикт `CHECKED`. По спеке это законно (rule 0, `docs/10-SPEC-v0.1.md:220-224`), по схеме — нет: валидирующая по схеме третья сторона получает другой контракт. Хуже: отчёт не печатает ни офсета, ни найденного региона, ни контекста, поэтому «anchored» нельзя перепроверить из отчёта — только повторив поиск вручную.

### Мелочи

**10.** `README.md:109` — «`examples/` — three statements: one that passes, one with opposite positions, one with a broken anchor», фактически 12 файлов (`tools/lexspec_status.py` печатает `examples: 12`).

**11.** `README.md:10` — «The checker never outputs the word "legal"», но каждый отчёт печатает `not_claimed … legal validity` (`tools/lexcheck.py:195`). Намерение верное, утверждение — ложное.

**12.** Мёртвый цикл `tools/lexcheck.py:1441-1443`: `for aid, atom in atoms.items(): if atom.get("applies") is False and status.get(aid) == "neither": continue` — тело ничего не делает. Похоже на недописанную семантику applicability (D4), оставленную без последствий.

**13.** `series[].path` не проходит `_is_repo_relative`: `tools/lexcheck.py:1161` делает `root / Path(declared)`, поэтому абсолютный путь или `..` пройдёт (для `corpus.text` такая проверка есть — `tools/lexcheck.py:382-383`, `:584-588`); схема тоже не ограничивает `seriesRef.path` (`schemas/statement-0.1.json:492-494`).

**14.** `docs/11-REFUSAL-CODES.md` требует, чтобы `detail` кода `S2_SPAN_NOT_FOUND` говорил, встречается ли span в **сыром** тексте; код добавляет это только при `raw_hit == 0 and len(needle) != len(span)` (`tools/lexcheck.py:977-981`), то есть в остальных случаях «must» не выполняется.

**15.** `tools/lexspec_status.py:47-97` всегда возвращает 0: строка `digests match declarations: NO` не роняет CI, и в `guards.yml` этот шаг сознательно не ассертится («printed for the log, not asserted»). Единственная защита от расхождения — `run_tests.py`, который проверяет хеши только тех корпусов, что уже объявлены в утверждениях; файл, который никто не цитирует, не проверяется нигде.

**16.** `coverage` сравнивается с порогом уже после `round(…, 3)` (`tools/lexcheck.py:1646-1648`), то есть `THIN_COVERAGE` решается по округлённому числу. Практически недостижимо (нужно ≥1000 атомов, чтобы попасть в окно `[0.7995, 0.8)`), отмечаю как теоретическое.

## Пять пунктов, которые я бы сделал первыми

1. **Валидировать `examples/*.json` схемой в CI** (один шаг `jsonschema` в `guards.yml`) и починить `segments` в 10/11/12 — сейчас три из двенадцати поставляемых примеров нарушают опубликованную схему, и ни один гейт этого не замечает.
2. **Заземлить `series[].basis`** через тот же S2-механизм (span в объявленном корпусе) — или убрать `basis` из схемы и из текста претензий. Сегодня число закрывает атом (`examples/10`, атом `a2`) с основанием, которого нет в корпусе.
3. **Починить вывод:** `sys.stdout.reconfigure(encoding="utf-8")` (или `ensure_ascii=True` для JSON) и отдельный код возврата для «не смог напечатать», чтобы крах не выглядел как REFUSED.
4. **Сверять `revision` с шапкой файла и печатать в отчёт блок `corpus{id, path, text_sha256, revision}`** — иначе «corpus@revision» в вердикте остаётся авторской строкой, которую никто не проверяет, а JSON-отчёт не называет проверенные байты.
5. **Либо реализовать `prefix`/`suffix` и правило «<40 символов ⇒ контекст обязателен», либо убрать их из спеки** и переписать `S2_SPAN_AMBIGUOUS` и слово «anchored» в терминах того, что код реально проверяет; заодно перегенерировать `tools/SELFTEST.md` в CI, чтобы опубликованные хеши не отставали от дерева.

## Чего я не проверял

- **Юридическую точность корпусов.** Сети не было; сверить `gk-rf-395-2026-10-28.txt` с pravo.gov.ru/ConsultantPlus и `gdpr-art17` с EUR-Lex CELEX 32016R0679 я не мог. Вопрос «та ли это редакция на 2026-10-28» остаётся открытым — я проверил только то, что дата редакции ничем не связана с текстом.
- **Арифметику L5 против первоисточника.** Тесты `tests/run_tests.py` проходят, но суммы/дни я не сверял с решением суда, на которое ссылаются комментарии и `lab/series/`.
- **Hohfeld-семантику конкретных атомов** (правильно ли выбран `duty`/`right` у конкретной стороны, корректны ли `temporal`-границы) — это содержательный юридический разбор, а не проверка кодировки.
- **`interop/*` и большую часть `lab/*`** (включая `check-spec.py`, `check-prose-numbers.py`, `check-hohfeld.py`) — не открывал, видел только совпадения по grep в первых двух; утверждения про flowguard и про «53 подхода» не проверял.
- **Историю.** В репозитории один коммит (`git rev-list --count HEAD` = 1), поэтому «append-only» записи `lab/` и вопрос «был ли SELFTEST корректен на момент коммита» проверить нельзя.
- **Поведение на Ubuntu/Python 3.11** (локально Windows/3.13): расхождение вывода по кодировке в CI не воспроизводил. `docs/` прочитаны выборочно — около 6 файлов из 40.
