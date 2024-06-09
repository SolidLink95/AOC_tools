extern crate bindgen;

use std::env;
use std::path::PathBuf;

fn main() {
    
    // Tell cargo to invalidate the built crate whenever the wrapper changes
    // println!("cargo:rerun-if-changed=wrapper.h");

    // Tell cargo to look for native libraries in the specified directory
    println!("cargo:rustc-link-search=native=lib");

    // Tell cargo to tell rustc to link the system bzip2
    // shared library.
    println!("cargo:rustc-link-lib=static=G1tLib");
    // let clang_path = "C:/Program Files/LLVM/bin/clang.exe"; // Update this path if necessary
    // env::set_var("CLANG_PATH", clang_path);

    // The bindgen::Builder is the main entry point
    // to bindgen, and lets you build up options for
    // the resulting bindings.
    // let bindings = bindgen::Builder::default()
    //     .header("wrapper.h")
        // .clang_arg("-I./cpp") // Ensure correct include path
        // .clang_arg("-I../../src") // Ensure correct include path
        // .clang_arg("-I../../eternity_common") // Ensure correct include path
        // .clang_arg("-IC:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.40.33807/include") // Ensure correct include path
        // .clang_arg("-IC:/Program Files (x86)/Windows Kits/10/Include/10.0.22000.0/ucrt") // Ensure correct include path
        // .clang_arg("-IC:/Program Files (x86)/Windows Kits/10/Include/10.0.22000.0/shared") // Ensure correct include path
        // .clang_arg("-IC:/Program Files (x86)/Windows Kits/10/Include/10.0.22000.0/um") // Ensure correct include path
    //     .clang_arg("-fms-extensions") // Use this for MSVC extensions
    //     .clang_arg("-fms-compatibility") // Use this for MSVC compatibility
    //     .clang_arg("-xc++") // Force C++ parsing
    //     .generate()
    //     // Unwrap the Result and panic on failure.
    //     .expect("Unable to generate bindings");

    // // Write the bindings to the $OUT_DIR/bindings.rs file.
    // let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    // bindings
    //     .write_to_file(out_path.join("bindings.rs"))
    //     .expect("Couldn't write bindings!");
}
