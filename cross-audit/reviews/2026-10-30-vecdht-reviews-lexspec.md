# Аудит от VecDHT — lexspec, 2026-10-30, коммит **6f71c22**

Клон `mak777uh/lexspec`, ветка `main` на `6f71c22` (свежесть пина проверена их же
`lab/check-audit-freshness.py`: 0 дней, предел 3). Рабочее дерево не менял; все прогоны — из корня
клона, Windows, Python 3.13.11 (в CI заявлен 3.11 / ubuntu — обе находки ниже от версии не зависят).

## Что запускал

| команда | результат |
|---|---|
| `python tests/run_tests.py` | `Ran 74 tests`, OK |
| `python lab/check-examples-schema.py` | 12 example(s), 0 violation(s) |
| `python tools/check_examples.py` | 12 examples match the recorded expectations |
| `python lab/check-spec.py` | clean — codes, fields, relations, squares, verdicts, examples, glossary and refs agree |
| `python lab/selftest-checkspec.py` | 4/4 mutations caught |
| `python tests/run_span_tests.py` | `Ran 6 tests`, OK |
| `python lab/check-secrets.py` | clean (103 text files scanned) |
| `python lab/check-prose-numbers.py` | 3 claim(s) agree with the tree (65.8 s) |
| `python lab/selftest-prose.py` | 10/10 checks behaved as required |
| `python lab/check-hohfeld.py` | L1…L8 hold — the table is the algebra |
| `python lab/selftest-hohfeld.py` | 4/4 checks behaved as required |
| `python tools/lexspec_status.py` | rc 0 |

Набор зелёный целиком. Дальше — то, чего зелёный набор не видит.

## Находки

### 1. `QuantityLayer` определён дважды; состав набора зависит от способа запуска (minor)

`tests/run_tests.py` содержит два класса с одним именем: строка 752 (8 тестов) и строка 867
(5 тестов, подмножество первого). Между ними, на строке 862, стоит
`if __name__ == "__main__": unittest.main(verbosity=2)`.

- `python tests/run_tests.py` → `Ran 74`, OK: запуск как скрипта доходит до `unittest.main()` до
  второго определения, поэтому работают все 8 тестов первого класса; `unittest.main()` завершает
  процесс, и строка 867 при этом исполнении не достигается.
- `cd tests && python -m unittest run_tests` → `Ran 71`, OK: модуль импортируется, блок `__main__`
  пропускается, второй класс затирает первый в пространстве имён модуля — и три теста исчезают
  молча, без единого красного сигнала.

Исчезают ровно те три, что проверяют арифметику процентов, ради которой слой quantities и написан:
`test_the_total_reproduces_the_judgment`, `test_a_payment_reduces_the_base_from_the_next_day`,
`test_the_year_is_cut_only_where_its_length_changes`.

CI сегодня зовёт `python tests/run_tests.py` (`.github/workflows/guards.yml:41`), поэтому текущий
зелёный честен. Но любой импортный раннер (pytest, `python -m unittest`, coverage) теряет три
проверки; фикс — одна строка: перенести блок `if __name__` в конец файла или переименовать второй
класс.

Воспроизвести:

```
grep -n "^class QuantityLayer\|^if __name__" tests/run_tests.py    # 752, 862, 867
python tests/run_tests.py 2>&1 | tail -3                           # Ran 74 tests
cd tests && python -m unittest run_tests 2>&1 | tail -3            # Ran 71 tests
```

### 2. Путь «output failure → exit 3» описан, но в коде его нет (minor)

`tools/lexcheck.py:1911-1922` заводит `OutputFailure` («carries exit code 3, never 1») и `_emit` —
единственную функцию, которая это исключение поднимает. Но `_emit` нигде не вызывается: отчёты
печатаются напрямую через `print(...)` в конце `main` (строки 1986 и 1988). `except OutputFailure`
в файле нет; `return 3` и `sys.exit(3)` тоже нет.

То есть документированного сигнала «3» не существует, а если бы исключение и возникло, оно вышло бы
неперехваченным трейсбеком с кодом 1 — тем же сигналом, что `REFUSED`, ровно та путаница, ради
устранения которой строка 3 в `docs/30-REPO-WALK.md` §1 и заводилась. Там же сказано «output
failures raise `OutputFailure` and are meant to exit 3»; в §1 «Still open» (строка 283) честно
признано, что пути нет теста, — но не сказано, что путь недостижим. Разница существенна:
непроверенный путь — долг, несуществующий путь — ложное утверждение о коде.

Сам перенос кодировки починкой остаётся: `_force_utf8_stdio()` (строка 1934) действительно
перестраивает stdout/stderr на UTF-8, и воспроизведение из строки 3 печатает отчёт. Не хватает
только второго плеча — проводки `_emit` и обработчика. Минимальный фикс: завернуть два `print` в
`_emit`, обернуть `main()` в `try/except OutputFailure: return 3`, добавить посадку с поддельным
потоком, чей `write` бросает `UnicodeEncodeError`.

Воспроизвести:

```
grep -n "OutputFailure\|_emit(" tools/lexcheck.py          # только определение, raise — ни одного вызова
grep -n "return 3\|sys.exit(3)" tools/lexcheck.py           # пусто
python -c "import sys; sys.path.insert(0,'tools'); import lexcheck; raise lexcheck.OutputFailure('x')"; echo rc=$?
                                                            # traceback, rc=1
```

## Проверено; находкой не стало

- **`lab/experiments.jsonl`, строка E-0002.** Её `statement.sha256` (`0650f659…`) не совпадает с
  текущим `examples/08-gk-rf-395.lex.json` (`9a2c6450…`). Проверил историю файла: `0650f659…` — это
  его блоб в `a2c1552`, а в `641c90a` пример изменён. Запись честно фиксирует версию на момент
  записи, ошибки в ней нет. Но ни один страж не пересчитывает эти digest'ы: дрейф виден только
  вручную, и E-0002 сейчас описывает не тот файл, который лежит в дереве. Кандидат на правило —
  «digest из experiments.jsonl обязан резолвиться в какой-либо блоб» либо поле `superseded_by`.
  Воспроизвести:
  ```
  python - <<'PY'
  import hashlib, json, pathlib, subprocess
  row = next(json.loads(l) for l in open('lab/experiments.jsonl', encoding='utf-8') if json.loads(l)['id'] == 'E-0002')
  print('row', row['statement']['sha256'])
  print('now', hashlib.sha256(pathlib.Path('examples/08-gk-rf-395.lex.json').read_bytes()).hexdigest())
  for c in subprocess.run(['git','log','--format=%h','--follow','--','examples/08-gk-rf-395.lex.json'],
                          capture_output=True, text=True).stdout.split():
      blob = subprocess.run(['git','show',f'{c}:examples/08-gk-rf-395.lex.json'], capture_output=True).stdout
      print(c, hashlib.sha256(blob).hexdigest()[:16])
  PY
  ```
- **`not_claimed`: 3 против 7.** `docs/10-SPEC-v0.1.md` §9 показывает три строки после «Every report …
  carries:», живой отчёт несёт семь (те же три плюс четыре, перечисленные в `docs/30-REPO-WALK.md`
  §1, строка 7). Ложного утверждения нет — три входят в семь, — но блок в спеке читается как
  исчерпывающий. Стоит написать «carries at least».
- **Таблицы в документации.** Число ячеек в строках каждой markdown-таблицы сверил: расхождений 0.
- **`tools/lexspec_status.py`.** rc 0, статус-блок печатается, чисел, противоречащих дереву, не
  нашёл.

## Границы

- Не запускал GitHub Actions и не смотрел статус прогонов: только прочитал workflow.
- Не проверял чекер под Python 3.11 и на Linux — прогоны локальные, Windows, 3.13.
- Не судил о юридическом содержании (Хофельд, якоря) — только о механике подтверждения.
- Входящие ревью в `cross-audit/` не оценивал: это чужой текст, а не свидетельство.
