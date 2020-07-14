use serde_json::{json, Value};
use std::error::Error;
use std::net::TcpStream;
use std::str::FromStr;
use structopt::StructOpt;
use num_bigint_dig::*;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "Walkie-Talkie",
    about = "The talker of the secure walkie-talkie protocol."
)]
struct Opt {
    #[structopt(short, long, default_value = "127.0.0.1")]
    ip: String,

    #[structopt(short, long, default_value = "8123")]
    port: u16,

    #[structopt(short, long)]
    sandbox: bool
}

fn main() -> Result<(), Box<dyn Error>> {
    let opt = Opt::from_args();

    if opt.sandbox {
        let i = BigUint::from_str("5")?;
        let j = BigUint::from_str("8")?;
        let m = BigUint::from_str("13")?;

        assert_eq!(i.mod_inverse(m).unwrap(), j.to_bigint().unwrap());

        return Ok(());
    }

    // Format supplied options into address.
    let addr = format!("{}:{}", opt.ip, opt.port);

    // Connect to address.
    let mut stream = TcpStream::connect(&addr)?;

    // Construct and send first message.
    let m1 = json!({ "msg": "this is the request" });
    protocol::send_data(&mut stream, m1.to_string().as_bytes())?;

    // Receive and convert data into second message.
    let m2_data = protocol::recv_data(&mut stream)?;
    let m2: Value = serde_json::from_str(std::str::from_utf8(&m2_data)?)?;

    println!("m2 = {}", serde_json::to_string_pretty(&m2)?);

    // Construct third message.
    let m3 = json!({ "msg": "this is the tag" });
    protocol::send_data(&mut stream, m3.to_string().as_bytes())?;

    Ok(())
}