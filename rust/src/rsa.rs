use num_bigint::BigUint;

/// RSA encryption using BigUints.
///
/// # Arguments
/// * `m` - The "plaintext" to encrypt.
/// * `e` - The RSA public exponent.
/// * `n` - The RSA public modulus.
pub fn encrypt(m: &BigUint, e: &BigUint, n: &BigUint) -> BigUint {
    m.modpow(e, n)
}

///// RSA decryption using BigUints.
/////
///// # Arguments
///// * `c` - The "ciphertext" to decrypt.
///// * `d` - The RSA private key.
/// * `n` - The RSA public modulus.
// pub fn decrypt(c: &BigUint, d: &BigUint, n: &BigUint) -> BigUint {
//     c.modpow(d, n)
// }

/// RSA signing using BigUints.
///
/// # Arguments
/// * `m` - The "plaintext" to sign.
/// * `d` - The RSA private key.
/// * `n` - The RSA public modulus.
pub fn sign(m: &BigUint, d: &BigUint, n: &BigUint) -> BigUint {
    m.modpow(d, n)
}

///// RSA verification using BigUints.
/////
///// # Arguments
///// * `s` - The "signature" to verify.
///// * `e` - The RSA public exponent.
///// * `n` - The RSA public modulus.
///// pub fn verify(s: &BigUint, e: &BigUint, n: &BigUint) -> BigUint {
//     s.modpow(e, n)
// }
