use pyo3::prelude::*;
use image::{imageops::FilterType, DynamicImage, GenericImageView, ImageBuffer, ImageFormat, Rgba};
use ddsfile::{AlphaMode, D3DFormat, Dds, DxgiFormat, NewDxgiParams, D3D10ResourceDimension};
use std::{error::Error, os::raw};
mod DdsFormatParser;
use DdsFormatParser::dds_to_dxgi_format;

#[pyfunction]
fn png_to_dds(png_data: Vec<u8>, format: &str, mipmaps_count: u32, width: u32, height: u32) -> PyResult<Vec<u8>> {
    // Decode PNG
    let img = image::load_from_memory_with_format(&png_data, ImageFormat::Png)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to decode PNG: {}", e)))?;

    // Resize the image if dimensions don't match
    let img = if img.width() != width || img.height() != height {
        img.resize_exact(width, height, FilterType::Lanczos3)
    } else {
        img
    };

    let rgba_image = img.to_rgba8();
    let raw_rgba = rgba_image.as_raw().clone();

    // Choose DXGI format based on input
    let dxgi_format = dds_to_dxgi_format(format.to_lowercase().as_str()).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get proper format: {}", e)))?;

    // Create DDS object with initial settings
    let mut dds = Dds::new_dxgi(NewDxgiParams {
        height,
        width,
        depth: None,
        format: dxgi_format,
        mipmap_levels: Some(mipmaps_count),
        array_layers: Some(1),
        is_cubemap: false,
        caps2: None,
        resource_dimension: D3D10ResourceDimension::Texture2D,
        alpha_mode: AlphaMode::Unknown,
    }).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create DDS: {}", e)))?;

    // Generate mipmaps and add them to the DDS
    let mut mipmaps = Vec::new();
    let mut current_level = raw_rgba.clone();
    let mut current_width = width;
    let mut current_height = height;

    for _ in 0..mipmaps_count {
        mipmaps.push(current_level.clone());

        if current_width > 1 || current_height > 1 {
            current_width = (current_width / 2).max(1);
            current_height = (current_height / 2).max(1);
            current_level = image::imageops::resize(
                &DynamicImage::ImageRgba8(image::RgbaImage::from_raw(current_width * 2, current_height * 2, current_level).unwrap()),
                current_width,
                current_height,
                FilterType::Lanczos3
            ).as_raw().clone();
        } else {
            break;
        }
    }

    // Set mipmaps data manually
    // let mut offset = 0;
    // for level in &mipmaps {
    //     let row_pitch = (current_width * 4).max(1);
    //     let size = (row_pitch * current_height) as usize;

    //     let mut slice = dds.get_mut_slice(offset, size).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get DDS slice: {}", e)))?;
    //     slice.copy_from_slice(level);

    //     offset += size;
    //     current_width = (current_width / 2).max(1);
    //     current_height = (current_height / 2).max(1);
    // }

    // Encode DDS to bytes
    let mut dds_bytes = Vec::new();
    dds.write(&mut dds_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to write DDS: {}", e)))?;

    Ok(dds_bytes)
}

#[pyfunction]
fn dds_to_dds(dds_data: Vec<u8>, format: &str, mipmaps_count: u32, width: u32, height: u32) -> PyResult<Vec<u8>> {
    // Load DDS
    let dds = Dds::read(&dds_data[..])
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to read DDS: {}", e)))?;

    // Extract raw data from the DDS
    let raw_data = dds.get_data(0).unwrap_or_default();
    if raw_data.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get DDS data"));
    }
        //.ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get DDS data"))?;

    // Create image from DDS raw data
    let dds_image = ImageBuffer::<Rgba<u8>, Vec<u8>>::from_raw(dds.get_width(), dds.get_height(), raw_data.to_vec())
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create image from DDS data"))?;
    
    // let img = DynamicImage::ImageRgba8(dds_image);
        // .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create image from DDS data"))?;
    let img = DynamicImage::ImageRgba8(dds_image);

    // Resize the image if dimensions don't match
    let img = if img.width() != width || img.height() != height {
        img.resize_exact(width, height, FilterType::Lanczos3)
    } else {
        img
    };

    let rgba_image = img.to_rgba8();
    let raw_rgba = rgba_image.as_raw().clone();

    // Choose DXGI format based on input
    let dxgi_format = dds_to_dxgi_format(format.to_lowercase().as_str())?;

    // Create DDS object with initial settings
    let mut new_dds = Dds::new_dxgi(NewDxgiParams {
        height,
        width,
        depth: None,
        format: dxgi_format,
        mipmap_levels: Some(mipmaps_count),
        array_layers: Some(1),
        is_cubemap: false,
        caps2: None,
        resource_dimension: D3D10ResourceDimension::Texture2D,
        alpha_mode: AlphaMode::Unknown,
    }).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create DDS: {}", e)))?;

    // Generate mipmaps and add them to the DDS
    let mut mipmaps = Vec::new();
    let mut current_level = raw_rgba.clone();
    let mut current_width = width;
    let mut current_height = height;

    for _ in 0..mipmaps_count {
        mipmaps.push(current_level.clone());

        if current_width > 1 || current_height > 1 {
            current_width = (current_width / 2).max(1);
            current_height = (current_height / 2).max(1);
            current_level = image::imageops::resize(
                &DynamicImage::ImageRgba8(image::RgbaImage::from_raw(current_width * 2, current_height * 2, current_level).unwrap()),
                current_width,
                current_height,
                FilterType::Lanczos3
            ).as_raw().clone();
        } else {
            break;
        }
    }

    // new_dds.set_data(&mipmaps)
    //     .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to set mipmaps: {}", e)))?;

    // Encode DDS to bytes
    let mut dds_bytes = Vec::new();
    new_dds.write(&mut dds_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to write DDS: {}", e)))?;

    Ok(dds_bytes)
}

#[pymodule]
fn png_to_dds_module(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(png_to_dds, m)?)?;
    m.add_function(wrap_pyfunction!(dds_to_dds, m)?)?;
    Ok(())
}