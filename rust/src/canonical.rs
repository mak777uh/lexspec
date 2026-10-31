//! Canonical JSON, as spec §3 defines it, with a hand-written parser.
//!
//! Why not `serde_json`: (a) the primary implementation must not need a supply chain to state its own identity, and
//! (b) duplicate keys are *refused* here — `serde_json` silently keeps the last one, and spec §3 says a document with
//! two identical keys is not a document. That difference is exactly the kind of thing this implementation exists to
//! make visible.
//!
//! Canonical rules implemented:
//!   * strings: RFC 8785 §3.2.2 escaping — `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, other control characters as
//!     `\u00XX`, everything else literal UTF-8;
//!   * object keys sorted by Unicode code point, recursively;
//!   * no whitespace between tokens;
//!   * numbers: integers only, leading zeros and `-0` refused; a float is refused with its own message;
//!   * the top level may be any value, and the output has no trailing newline.

use std::collections::BTreeMap;
use std::fmt::Write as _;

#[derive(Debug, PartialEq, Eq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i128),
    Str(String),
    Array(Vec<Value>),
    Object(BTreeMap<String, Value>),
}

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    UnexpectedEnd,
    ExpectedValue(usize),
    UnterminatedString(usize),
    BadEscape(usize),
    BadNumber(usize),
    FloatForbidden(usize),
    TrailingData(usize),
    DuplicateKey(String),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Error::UnexpectedEnd => write!(f, "unexpected end of input"),
            Error::ExpectedValue(pos) => write!(f, "expected a value at byte {pos}"),
            Error::UnterminatedString(pos) => write!(f, "unterminated string starting at byte {pos}"),
            Error::BadEscape(pos) => write!(f, "invalid escape at byte {pos}"),
            Error::BadNumber(pos) => write!(f, "invalid number at byte {pos}"),
            Error::FloatForbidden(pos) => write!(
                f,
                "a floating-point number at byte {pos}: the canonical form is integers only, because a float cannot \
                 be hashed reproducibly (spec §3)"
            ),
            Error::TrailingData(pos) => write!(f, "trailing data after the value at byte {pos}"),
            Error::DuplicateKey(key) => write!(
                f,
                "duplicate object key {key:?}: two identical keys are two claims about one field, and keeping the
                 last one silently is how a document lies about itself"
            ),
        }
    }
}

pub struct Parser<'a> {
    bytes: &'a [u8],
    pos: usize,
}

impl<'a> Parser<'a> {
    pub fn new(text: &'a str) -> Self {
        Self { bytes: text.as_bytes(), pos: 0 }
    }

    fn skip_ws(&mut self) {
        while let Some(byte) = self.bytes.get(self.pos) {
            match byte {
                b' ' | b'\t' | b'\n' | b'\r' => self.pos += 1,
                _ => break,
            }
        }
    }

    fn peek(&self) -> Option<u8> {
        self.bytes.get(self.pos).copied()
    }

    pub fn parse_document(&mut self) -> Result<Value, Error> {
        let value = self.parse_value()?;
        self.skip_ws();
        if self.pos != self.bytes.len() {
            return Err(Error::TrailingData(self.pos));
        }
        Ok(value)
    }

    fn parse_value(&mut self) -> Result<Value, Error> {
        self.skip_ws();
        match self.peek() {
            None => Err(Error::UnexpectedEnd),
            Some(b'{') => self.parse_object(),
            Some(b'[') => self.parse_array(),
            Some(b'"') => Ok(Value::Str(self.parse_string()?)),
            Some(b't') => self.expect_literal("true", Value::Bool(true)),
            Some(b'f') => self.expect_literal("false", Value::Bool(false)),
            Some(b'n') => self.expect_literal("null", Value::Null),
            Some(b'-') | Some(b'0'..=b'9') => self.parse_number(),
            Some(_) => Err(Error::ExpectedValue(self.pos)),
        }
    }

    fn expect_literal(&mut self, literal: &str, value: Value) -> Result<Value, Error> {
        if self.bytes[self.pos..].starts_with(literal.as_bytes()) {
            self.pos += literal.len();
            Ok(value)
        } else {
            Err(Error::ExpectedValue(self.pos))
        }
    }

    fn parse_object(&mut self) -> Result<Value, Error> {
        self.pos += 1; // '{'
        let mut map = BTreeMap::new();
        self.skip_ws();
        if self.peek() == Some(b'}') {
            self.pos += 1;
            return Ok(Value::Object(map));
        }
        loop {
            self.skip_ws();
            if self.peek() != Some(b'"') {
                return Err(Error::ExpectedValue(self.pos));
            }
            let key = self.parse_string()?;
            self.skip_ws();
            if self.peek() != Some(b':') {
                return Err(Error::ExpectedValue(self.pos));
            }
            self.pos += 1;
            let value = self.parse_value()?;
            if map.insert(key.clone(), value).is_some() {
                return Err(Error::DuplicateKey(key));
            }
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(Value::Object(map));
                }
                _ => return Err(Error::ExpectedValue(self.pos)),
            }
        }
    }

    fn parse_array(&mut self) -> Result<Value, Error> {
        self.pos += 1; // '['
        let mut items = Vec::new();
        self.skip_ws();
        if self.peek() == Some(b']') {
            self.pos += 1;
            return Ok(Value::Array(items));
        }
        loop {
            items.push(self.parse_value()?);
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b']') => {
                    self.pos += 1;
                    return Ok(Value::Array(items));
                }
                _ => return Err(Error::ExpectedValue(self.pos)),
            }
        }
    }

    fn parse_string(&mut self) -> Result<String, Error> {
        let start = self.pos;
        self.pos += 1; // opening quote
        let mut out = String::new();
        loop {
            let byte = self.peek().ok_or(Error::UnterminatedString(start))?;
            match byte {
                b'"' => {
                    self.pos += 1;
                    return Ok(out);
                }
                b'\\' => {
                    self.pos += 1;
                    let escape = self.peek().ok_or(Error::UnterminatedString(start))?;
                    self.pos += 1;
                    match escape {
                        b'"' => out.push('"'),
                        b'\\' => out.push('\\'),
                        b'/' => out.push('/'),
                        b'b' => out.push('\u{8}'),
                        b'f' => out.push('\u{c}'),
                        b'n' => out.push('\n'),
                        b'r' => out.push('\r'),
                        b't' => out.push('\t'),
                        b'u' => {
                            let hex = self
                                .bytes
                                .get(self.pos..self.pos + 4)
                                .ok_or(Error::BadEscape(self.pos))?;
                            let text = std::str::from_utf8(hex).map_err(|_| Error::BadEscape(self.pos))?;
                            let code = u16::from_str_radix(text, 16).map_err(|_| Error::BadEscape(self.pos))?;
                            self.pos += 4;
                            // surrogate pairs: a lone half is a defect, not a character
                            let ch = if (0xD800..0xDC00).contains(&code) {
                                if self.bytes.get(self.pos..self.pos + 2) != Some(b"\\u") {
                                    return Err(Error::BadEscape(self.pos));
                                }
                                let low_hex = self
                                    .bytes
                                    .get(self.pos + 2..self.pos + 6)
                                    .ok_or(Error::BadEscape(self.pos))?;
                                let low_text =
                                    std::str::from_utf8(low_hex).map_err(|_| Error::BadEscape(self.pos))?;
                                let low = u16::from_str_radix(low_text, 16)
                                    .map_err(|_| Error::BadEscape(self.pos))?;
                                if !(0xDC00..0xE000).contains(&low) {
                                    return Err(Error::BadEscape(self.pos));
                                }
                                self.pos += 6;
                                let combined =
                                    0x10000 + (((code - 0xD800) as u32) << 10) + (low - 0xDC00) as u32;
                                char::from_u32(combined).ok_or(Error::BadEscape(self.pos))?
                            } else {
                                char::from_u32(code as u32).ok_or(Error::BadEscape(self.pos))?
                            };
                            out.push(ch);
                        }
                        _ => return Err(Error::BadEscape(self.pos - 1)),
                    }
                }
                _ => {
                    // copy one UTF-8 character, not one byte
                    let remaining = std::str::from_utf8(&self.bytes[self.pos..])
                        .map_err(|_| Error::UnterminatedString(start))?;
                    let ch = remaining.chars().next().ok_or(Error::UnterminatedString(start))?;
                    out.push(ch);
                    self.pos += ch.len_utf8();
                }
            }
        }
    }

    fn parse_number(&mut self) -> Result<Value, Error> {
        let start = self.pos;
        if self.peek() == Some(b'-') {
            self.pos += 1;
        }
        while let Some(byte) = self.peek() {
            match byte {
                b'0'..=b'9' => self.pos += 1,
                b'.' | b'e' | b'E' => return Err(Error::FloatForbidden(self.pos)),
                _ => break,
            }
        }
        let text = std::str::from_utf8(&self.bytes[start..self.pos]).map_err(|_| Error::BadNumber(start))?;
        let value: i128 = text.parse().map_err(|_| Error::BadNumber(start))?;
        if text == "-0" {
            return Err(Error::BadNumber(start));
        }
        Ok(Value::Int(value))
    }
}

fn escape_into(out: &mut String, text: &str) {
    out.push('"');
    for ch in text.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{8}' => out.push_str("\\b"),
            '\u{c}' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

fn emit(value: &Value, out: &mut String) {
    match value {
        Value::Null => out.push_str("null"),
        Value::Bool(true) => out.push_str("true"),
        Value::Bool(false) => out.push_str("false"),
        Value::Int(number) => {
            let _ = write!(out, "{number}");
        }
        Value::Str(text) => escape_into(out, text),
        Value::Array(items) => {
            out.push('[');
            for (index, item) in items.iter().enumerate() {
                if index > 0 {
                    out.push(',');
                }
                emit(item, out);
            }
            out.push(']');
        }
        Value::Object(map) => {
            out.push('{');
            for (index, (key, item)) in map.iter().enumerate() {
                if index > 0 {
                    out.push(',');
                }
                escape_into(out, key);
                out.push(':');
                emit(item, out);
            }
            out.push('}');
        }
    }
}

/// Parse and re-emit in canonical form.
pub fn canonicalise(text: &str) -> Result<String, Error> {
    let mut parser = Parser::new(text);
    let value = parser.parse_document()?;
    let mut out = String::with_capacity(text.len());
    emit(&value, &mut out);
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keys_are_sorted_by_code_point_at_every_depth() {
        let input = r#"{"b":1,"a":{"z":2,"y":[{"q":1,"p":2}]}}"#;
        assert_eq!(canonicalise(input).unwrap(), r#"{"a":{"y":[{"p":2,"q":1}],"z":2},"b":1}"#);
    }

    #[test]
    fn whitespace_disappears() {
        assert_eq!(canonicalise(" { \"a\" : [ 1 , 2 ] } ").unwrap(), r#"{"a":[1,2]}"#);
    }

    #[test]
    fn floats_are_refused_with_their_own_message() {
        let error = canonicalise(r#"{"coverage":0.5}"#).unwrap_err();
        assert!(matches!(error, Error::FloatForbidden(_)));
    }

    #[test]
    fn duplicate_keys_are_refused() {
        let error = canonicalise(r#"{"a":1,"a":2}"#).unwrap_err();
        assert_eq!(error, Error::DuplicateKey("a".to_string()));
    }

    #[test]
    fn control_characters_are_escaped_and_unicode_is_literal() {
        assert_eq!(canonicalise("\"a\\u0001б\"").unwrap(), "\"a\\u0001б\"");
    }

    #[test]
    fn a_trailing_value_is_not_a_document() {
        assert!(matches!(canonicalise("{} {}"), Err(Error::TrailingData(_))));
    }
}
