mod bindings {
    include!("bindings.rs");
}
extern crate libc;
use bindings::{CResult, CBytes, G1tCompile, G1tDecompile, free_cresult};
use std::ffi::CStr;
use std::ptr;
use std::fs;
use std::io;

pub fn compile_g1t(dds_data: Vec<Vec<u8>>) -> Vec<u8> {
    let c_dds_data: Vec<*const u8> = dds_data.iter().map(|v| v.as_ptr()).collect();
    let c_dds_sizes: Vec<usize> = dds_data.iter().map(|v| v.len()).collect();

    unsafe {
        let result = G1tCompile(c_dds_data.as_ptr(), c_dds_sizes.as_ptr(), dds_data.len());
        std::slice::from_raw_parts(result.data, result.size).to_vec()
    }
}

pub fn decompile_g1t(g1t_data: Vec<u8>) -> (String, Vec<Vec<u8>>) {
    unsafe {
        // Call the C++ function
        let result = G1tDecompile(g1t_data.as_ptr(), g1t_data.len());

        // Convert C string to Rust string
        let metadata = CStr::from_ptr(result.metadata).to_string_lossy().into_owned();

        // Convert DDS data
        let mut dds_data = Vec::new();
        for i in 0..result.num_dds {
            // Read the raw pointers safely
            let dds_data_ptr = *result.dds_data.add(i);
            let dds_size = *result.dds_sizes.add(i);
            let dds_slice = std::slice::from_raw_parts(dds_data_ptr, dds_size);
            dds_data.push(dds_slice.to_vec());
        }

        // Free the C result to avoid memory leaks
        free_cresult(result);

        (metadata, dds_data)
    }
}



fn main() -> io::Result<()> {
    let g1tPath = "D:/coding/AOC_tools/src/g1ms/0cc1a2b4.g1t".to_string();
    let rawdata = fs::read(&g1tPath)?;
    let (metadata, dds_data) = G1T_rs::decompile_g1t(rawdata);

    // println!("Metadata:\n{}", &metadata);
    Ok(())
}
