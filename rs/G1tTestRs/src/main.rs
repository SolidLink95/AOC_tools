
use G1T_rs;
use std::fs;
use std::io;

fn main() -> io::Result<()> {
    let g1tPath = "D:/coding/AOC_tools/src/g1ms/0cc1a2b4.g1t".to_string();
    let rawdata = fs::read(&g1tPath)?;
    let (metadata, dds_data) = G1T_rs::decompile_g1t(rawdata);

    // println!("Metadata:\n{}", &metadata);
    Ok(())
}
