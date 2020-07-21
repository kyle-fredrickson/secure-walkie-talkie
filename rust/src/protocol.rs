use std::error::Error;
use std::io::prelude::*;
use std::net::TcpStream;

/// Sends bytes of data over a TCP stream.
///
/// # Arguments
///
/// * `stream` - A mutable reference to a TcpStream.
/// * `data` - A slice of bytes to send.
pub fn send_data(stream: &mut TcpStream, data: &[u8]) -> Result<(), Box<dyn Error>> {
    // Write the type and length (currently just the length).
    stream.write_all(format!("{:0>8}", data.len()).as_bytes())?;
    stream.flush()?;

    // Write the actual data.
    stream.write_all(&data)?;
    stream.flush()?;

    Ok(())
}

/// Receives bytes of data over a TcpStream.
///
/// # Arguments
///
/// * `stream` - A mutable reference to a TcpStream.
pub fn recv_data(stream: &mut TcpStream) -> Result<Vec<u8>, Box<dyn Error>> {
    // Read 8 bytes denoting string.
    let mut buf = [0u8; 8];
    stream.read(&mut buf)?;

    // Convert bytes into actual integer.
    let length: usize = std::str::from_utf8(&buf)?.parse()?;

    // Read in specified number of bytes.
    let mut data = vec![0u8; length];
    stream.read(&mut data)?;

    Ok(data)
}
