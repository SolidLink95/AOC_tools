// #![allow(non_camel_case_types)]

use std::os::raw::{c_char, c_uchar};
use libc::size_t;

/// Corresponds to CResult struct in C++.
#[repr(C)]
pub struct CResult {
    pub metadata: *const c_char,
    pub dds_data: *mut *mut c_uchar,
    pub dds_sizes: *mut size_t,
    pub num_dds: size_t,
}

/// Corresponds to CBytes struct in C++.
#[repr(C)]
pub struct CBytes {
    pub data: *const c_uchar,
    pub size: size_t,
}

extern "C" {
    pub fn G1tDecompile(
        g1t_data: *const c_uchar,
        g1t_size: size_t,
    ) -> CResult;

    pub fn free_cresult(result: CResult);

    pub fn G1tCompile(
        dds_data: *const *const c_uchar,
        dds_sizes: *const size_t,
        num_dds: size_t,
    ) -> CBytes;
}
