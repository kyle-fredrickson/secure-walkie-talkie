use serde_json::{json, Value};
use std::error::Error;
use std::net::TcpListener;
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "Walkie-Talkie",
    about = "The listener of the secure walkie-talkie protocol."
)]
struct Opt {
    #[structopt(short, long, default_value = "127.0.0.1")]
    ip: String,

    #[structopt(short, long, default_value = "8123")]
    port: u16,
}

fn main() -> Result<(), Box<dyn Error>> {
    let opt = Opt::from_args();

    // Format supplied options into address.
    let addr = format!("{}:{}", opt.ip, opt.port);

    // Bind to address.
    let listener = TcpListener::bind(&addr)?;

    // Accept on binded port to establish stream with client.
    let (mut stream, _addr) = listener.accept()?;

    // Receive and convert data into first message.
    let m1_data = protocol::recv_data(&mut stream)?;
    let m1: Value = serde_json::from_str(std::str::from_utf8(&m1_data)?)?;

    println!("m1 = {}", serde_json::to_string_pretty(&m1)?);

    // Construct and send second message.
    let m2 = json!({ "msg": "this is the response" });
    protocol::send_data(&mut stream, m2.to_string().as_bytes())?;

    // Receive and convert data into third message.
    let m3_data = protocol::recv_data(&mut stream)?;
    let m3: Value = serde_json::from_str(std::str::from_utf8(&m3_data)?)?;

    println!("m3 = {}", serde_json::to_string_pretty(&m3)?);

    Ok(())
}
