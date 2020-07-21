use rug::Integer;

/// RSA encryption using BigUints.
///
/// # Arguments
/// * `m` - The "plaintext" to encrypt.
/// * `e` - The RSA public exponent.
/// * `n` - The RSA public modulus.
pub fn encrypt(m: &Integer, e: &Integer, n: &Integer) -> Integer {
    m.clone().secure_pow_mod(e, n)
}

/// RSA decryption using BigUints.
///
/// # Arguments
/// * `c` - The "ciphertext" to decrypt.
/// * `d` - The RSA private key.
/// * `n` - The RSA public modulus.
pub fn decrypt(c: &Integer, d: &Integer, n: &Integer) -> Integer {
    c.clone().secure_pow_mod(d, n)
}

/// RSA signing using BigUints.
///
/// # Arguments
/// * `m` - The "plaintext" to sign.
/// * `d` - The RSA private key.
/// * `n` - The RSA public modulus.
pub fn sign(m: &Integer, d: &Integer, n: &Integer) -> Integer {
    m.clone().secure_pow_mod(d, n)
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
