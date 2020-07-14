# Rust Implementation

The Rust implementation of the secure walkie-talkie.

### Design

Two binaries: ```talker``` and ```listener```. The talker, through an extensive
protocol, securely sends the listener audio. The protocol is comprised of RSA
signing, Diffie-Hellman key exchange, and SHA-3 hash-based tagging and
verification.

### Building

To build both binaries:

    $ cargo build

### Usage

Start up ```listener``` in one terminal instance then ```talker``` in another.
This can be achieved by using the ```cargo run``` command.
