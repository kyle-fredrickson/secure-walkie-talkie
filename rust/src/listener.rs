use rug::{rand::RandState, integer::Order, Integer};
use serde_json::{json, Value};
use sha3::{Digest, Sha3_256};
use std::error::Error;
use std::net::TcpListener;
use structopt::StructOpt;

mod protocol;

mod rsa;
use rsa::{decrypt, verify};

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

    #[structopt(short, long)]
    test: bool
}

fn main() -> Result<(), Box<dyn Error>> {
    // Parse command-line options.
    let opt = Opt::from_args();

    // g is the Diffie-Hellman generator.
    let g = Integer::from_str_radix(
        "9677178152764243356585979556264224589944191744979699073371576738861236\
         5663820546922607619786124954900448084138704336019707101781113070799068\
         5744514558595068941725067952556006237862391064159647193542530329259333\
         4424851756939418426847120076462424229265080004033026690789716709345894\
         8676163784692008959171172634206184380581278989999081666391528267108503\
         9813609522242829719587993249808317734238106660385861768230295679126590\
         8390972444782203928717828427457583267560097495187522617809715033399571\
         0124142927808606451916188467080375525692807503004072582957175996256741\
         6958199028585508053574180142683126826804771118716296486230523760774389\
         7157494791542352379311268259974895147341335235499016003307513390038990\
         1582196141853936279863966997543171337135092681583084518153432642302837\
         0436056697857918994988629688023563560002153140124962200937852164145182\
         1610847931627295268929335901602846813690082539801509776517015975714046\
         5455848263618069464889478247144935435822126939965077545376582476552939\
         5288811662441509565199205733657279155210616750060391443188845224391244\
         5982465119470715706942563826139640100216780957119233780885476576542097\
         8318327126238727841787217270826207296485682133095572761510633060271315\
         2230040271215", 10
    )?;

    // p is the Diffie-Hellman prime.
    let p = Integer::from_str_radix(
        "2773513095749167337576358874942831569385761553923082020361322269992944\
         8489006798120232791463013505228500900024049333039459029366992215417394\
         0703109337560451078293297821188778260938274928421790028940882569457077\
         8270715497001472804773372159699487464437256876108641279314813575799288\
         0353560828726390302647822163531592190925834713707675874151479095828997\
         9709275760692869280803757520668776451222054720062078905947201506921948\
         2248258148634825249349597280042484353178956233483223727571140311838306\
         9497997993896536595853659564600179648675284862073335665278820295284039\
         2441154268228992660874384047813295938635270043470524847835602162062324\
         6182957756186469188241103927864116660349640671385022766484753851141361\
         3324705366794734356249759513986782234719409680441184269264165474240174\
         7019497972779105025866714266206768504640255640079527841905839126323963\
         3600041551667467165519541808705130094613958692430907777974227738480151\
         9284479867895217795687886082284763600753200413473134257852188910038101\
         0022934537091672256327978299054218233790927484338926431601990283936699\
         4034965244475466733634646851920984543901636177633543005383561910647171\
         8158178526713140623881625988429186051133467385983636059069118372099145\
         33050012879383", 10
    )?;

    // rsa_p is the private RSA prime p.
    let rsa_p = Integer::from_str_radix(
        "2798856292306279585730145950047639374630858739495795818841365329796739\
         0906121377268590319563545778111418862084880619765772346578436238215505\
         7141524890767793205117163931707678346358484017883363223877180735358481\
         6471363805139034383787208082977930405691501336933245568049894415294344\
         6789096589357348266059152209911675811869253104243164805630568530912397\
         8381566256958326159077487298931674630506678416903741217554579631158994\
         5339506160235148042021993613655367151877618653127946251476688278504795\
         8796490713613487790899355782642168910056836731629017454350084219866617\
         192892840458995035807583429597673775027701949562848240003", 10
    )?;

    // rsa_q is the private RSA prime q.
    let rsa_q = Integer::from_str_radix(
        "2631002797442685393814794411394178277292334408820922059670565569058228\
         7578930553031500311295857127175657668132667966309536601760669209178037\
         4455723862501270592068782553031061068834496324328017017659949262474168\
         1827033800136651208955074532129489742230077373486124599170001201274575\
         7647260492750795039231334945637488084777778047404754567194822950073686\
         4107738423955929847509435652482810459809189632083057058180924310587851\
         9023016665098914608397361259269680695520112395283647325285828693297992\
         5810525845973934112102623815593019477825322154739029747706323546766877\
         435942805607692940317841779871565175509326420748476158127", 10
    )?;

    // rsa_e is the public RSA exponent.
    let rsa_e = Integer::from_str_radix(
        "1304993590170532815564584313455331237783637816512705654360829774396135\
         7994954717322917425749364642943354291308521375017815197673634269952642\
         0648990703464945248532071716729673844568792726143091424684881888949619\
         8032642106528691368723413730466185004438451292576440955342411536470676\
         19323000920769040063242820133", 10
    )?;

    // rsa_pub is the public RSA key.
    let rsa_pub = Integer::from(&rsa_p * &rsa_q);

    // rsa_priv is the private RSA key.
    let p_minus_1 = Integer::from(&rsa_p - 1);
    let q_minus_1 = Integer::from(&rsa_q - 1);
    let totient = Integer::from(&p_minus_1 * &q_minus_1);
    let rsa_priv = rsa_e.clone().invert(&Integer::from(totient)).unwrap();

    // Format supplied options into address.
    let addr = format!("{}:{}", opt.ip, opt.port);

    // Bind to address.
    let listener = TcpListener::bind(&addr)?;

    // Accept on binded port to establish stream with client.
    let (mut stream, _addr) = listener.accept()?;

    // Receive and convert data into first message.
    let m1_data = protocol::recv_data(&mut stream)?;
    let m1: Value = serde_json::from_str(std::str::from_utf8(&m1_data)?)?;

    // Unpack session key 1.
    let ses1 = Integer::from_str_radix(m1["sess_key"].as_str().unwrap(), 10)?;

    // Unpack message 1 part a.
    let m1_a_int = decrypt(&ses1, &rsa_priv, &rsa_pub);
    let m1_a_bytes = m1_a_int.to_digits::<u8>(Order::MsfBe);
    let m1_a: Value = serde_json::from_str(std::str::from_utf8(m1_a_bytes.as_slice())?)?;

    // Unpack message 1 part c.
    // TODO: Finish porting Simon.
    let m1_c = &m1["payload"];

    // Unpack message 1 part b.
    let m1_b = &m1_c["agreement_data"];

    // Compute hash of m1_b and convert to integer.
    let m1_b_hash = Sha3_256::digest(m1_b.to_string().as_bytes());
    let m1_b_hash_int = Integer::from_digits(m1_b_hash.as_slice(), Order::MsfBe);

    // Verify signature 1.
    let sig_1 = Integer::from_str_radix(m1_c["signature"].as_str().unwrap(), 10)?;
    assert_eq!(verify(&sig_1, &rsa_e, &rsa_pub), m1_b_hash_int);

    // Compute hash of m1_a for the session key hash and convert to integer.
    let m1_a_hash = Sha3_256::digest(m1_a.to_string().as_bytes());
    let m1_a_hash_int = Integer::from_digits(m1_a_hash.as_slice(), Order::MsfBe);

    // Verify session key hash.
    let h = Integer::from_str_radix(m1_b["hash_sess_key"].as_str().unwrap(), 10)?;
    assert_eq!(h, m1_a_hash_int);

    // Unpack Diffie-Hellman public key.
    let dh_pub_a = Integer::from_str_radix(m1_b["diffie_pub_k"].as_str().unwrap(), 10)?;

    // Sanity check.
    // TODO: Remove check when finished.
    println!("key = {}", m1_a["key"]);
    println!("tod = {}", m1_a["tod"]);
    println!("hash_sess_key = {}", m1_a_hash_int);
    println!("diffie_pub_k = {}", dh_pub_a);

    // Start up random state (seed for now).
    // TODO: Remove seeding when done.
    let mut rng = RandState::new();

    if !opt.test {
        let seed = Integer::from(1234);
        rng.seed(&seed);
    }

    // s_b is a 256-bit random number.
    let s_b = Integer::from(Integer::random_bits(256, &mut rng));

    // d_b is a 4096-bit random number.
    let d_b = Integer::from(Integer::random_bits(4096, &mut rng));

    // dh_pub_a is the public Diffie-Hellman key.
    // TODO: Remove underscore since it'll be used.
    let _dh_pub_b = g.secure_pow_mod(&d_b, &p);

    // Construct message 2 part a.
    let m2 = json!({
        "key": s_b.to_string()
    });

    protocol::send_data(&mut stream, m2.to_string().as_bytes())?;

    // Receive and convert data into third message.
    let m3_data = protocol::recv_data(&mut stream)?;
    let m3: Value = serde_json::from_str(std::str::from_utf8(&m3_data)?)?;

    println!("m3 = {}", serde_json::to_string_pretty(&m3)?);

    Ok(())
}
