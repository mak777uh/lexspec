//! LexSpec — the Rust implementation. First slice: canonical form, and nothing else.
//!
//! The Python checker is the executable contract today (ADR-0002), and this binary exists to become the primary
//! implementation by agreeing with it **byte for byte**. So the first thing built is the only thing whose agreement
//! is meaningful without any parsing: the canonical serialisation and its digest.
//!
//! Canonical form (spec §3): UTF-8, LF, no BOM, object keys sorted by Unicode code point at every depth, no
//! insignificant whitespace, integers only — a float is refused, because a float cannot be hashed reproducibly.

mod canonical;
mod sha256;

use std::env;
use std::fs;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();
    match args.first().map(String::as_str) {
        Some("canonical") => match args.get(1) {
            Some(path) => match fs::read_to_string(path) {
                Ok(text) => match canonical::canonicalise(&text) {
                    Ok(canonical) => {
                        // same shape as the Python tool: the canonical text, a newline, then the digest
                        println!("{canonical}");
                        println!("sha256 {}", sha256::hex_digest(canonical.as_bytes()));
                        ExitCode::SUCCESS
                    }
                    Err(error) => {
                        eprintln!("lexspec: {error}");
                        ExitCode::from(1)
                    }
                },
                Err(error) => {
                    eprintln!("lexspec: cannot read {path}: {error}");
                    ExitCode::from(2)
                }
            },
            None => {
                eprintln!("usage: lexspec canonical <statement.lex.json>");
                ExitCode::from(2)
            }
        },
        _ => {
            eprintln!("lexspec 0.1.0 — implemented: `canonical` (canonical form + sha256)");
            eprintln!("usage: lexspec canonical <statement.lex.json>");
            ExitCode::from(2)
        }
    }
}
