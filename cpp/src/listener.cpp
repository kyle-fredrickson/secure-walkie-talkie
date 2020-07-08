#include "audio.h"
#include "being.h"
#include "bigint.h"
#include "ctr.h"
#include "database.h"
#include "rsa.h"
#include "sha3.h"
#include "server.h"
#include "util.h"
#include <chrono>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <vector>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#define OPTIONS   "hvp:"

void print_usage(char *program) {
  std::cerr <<
    "SYNOPSIS\n"
    "   Receive and play decrypted audio.\n"
    "   Audio is encrypted and sent by the talker program.\n"
    "\n"
    "USAGE\n";
  std::cerr <<  "   " << program << " [-hv] [-p port]\n"
    "\n"
    "OPTIONS\n"
    "   -h        Display program help and usage\n"
    "   -v        Display verbose program output\n"
    "   -p port   Specify port to send audio to (default: 8123)";
  std::cerr << std::endl;
  return;
}

int main(int argc, char **argv) {
  int opt = 0;
  int port = 8123;

  while ((opt = getopt(argc, argv, OPTIONS)) != -1) {
    switch (opt) {
    case 'h':
      print_usage(argv[0]);
      return 0;
    case 'v':
      verbose = true;
      break;
    case 'p':
      port = std::stoi(std::string(optarg));
      break;
    default:
      print_usage(argv[0]);
      return 1;
    }
  }

  /* BigInt rsa_p = */
  /*   "2558242469582035501706524463753018838309803881781857001971763341901227" */
  /*   "0340300855594212074923247689911718610163505692641867820444701812370173" */
  /*   "5525898001905536430570865039315690285675166428475762807811536727162992" */
  /*   "0305772531532469069453365483874838633698732318611688160741750010825263" */
  /*   "7511869060877536587297755903850209273785742271166231431228162520193681" */
  /*   "3909066826418765270711906189932098969307833186282133229043187609972729" */
  /*   "8865367430587564961177801815273046952421372685028147615202081569604502" */
  /*   "4080589201309573267638943136237630779099365885927657803100496536986260" */
  /*   "492978376671952740977481995731602392079816690339534580057"; */

  /* BigInt rsa_q = */
  /*   "1233070238404071309124783348472904156033722398443200795699277004389822" */
  /*   "5954890252026406230871808008085992289391971148090351792429794860251002" */
  /*   "8550324846212666243265057127081311832029782884980442847984826569430528" */
  /*   "2584291851188461372036778025264360207386850445948478911204028669743752" */
  /*   "2279437071203556679828598220391413465234687271006051853332790626446247" */
  /*   "0326512876846233289752047144201876557754451606054272499436707256171105" */
  /*   "7602061290759875893767412185402846072926106537045407361152402645485456" */
  /*   "6296268253124135166143766219065573770840153505019541660730502119784035" */
  /*   "80642487554654476205323952167492130031550280252570440627"; */

  BigInt rsa_p =
    "2798856292306279585730145950047639374630858739495795818841365329796739"
    "0906121377268590319563545778111418862084880619765772346578436238215505"
    "7141524890767793205117163931707678346358484017883363223877180735358481"
    "6471363805139034383787208082977930405691501336933245568049894415294344"
    "6789096589357348266059152209911675811869253104243164805630568530912397"
    "8381566256958326159077487298931674630506678416903741217554579631158994"
    "5339506160235148042021993613655367151877618653127946251476688278504795"
    "8796490713613487790899355782642168910056836731629017454350084219866617"
    "192892840458995035807583429597673775027701949562848240003";

  BigInt rsa_q =
    "2631002797442685393814794411394178277292334408820922059670565569058228"
    "7578930553031500311295857127175657668132667966309536601760669209178037"
    "4455723862501270592068782553031061068834496324328017017659949262474168"
    "1827033800136651208955074532129489742230077373486124599170001201274575"
    "7647260492750795039231334945637488084777778047404754567194822950073686"
    "4107738423955929847509435652482810459809189632083057058180924310587851"
    "9023016665098914608397361259269680695520112395283647325285828693297992"
    "5810525845973934112102623815593019477825322154739029747706323546766877"
    "435942805607692940317841779871565175509326420748476158127";

  BigInt rsa_e =
    "1304993590170532815564584313455331237783637816512705654360829774396135"
    "7994954717322917425749364642943354291308521375017815197673634269952642"
    "0648990703464945248532071716729673844568792726143091424684881888949619"
    "8032642106528691368723413730466185004438451292576440955342411536470676"
    "19323000920769040063242820133";

  BigInt dh_g =
    "9677178152764243356585979556264224589944191744979699073371576738861236"
    "5663820546922607619786124954900448084138704336019707101781113070799068"
    "5744514558595068941725067952556006237862391064159647193542530329259333"
    "4424851756939418426847120076462424229265080004033026690789716709345894"
    "8676163784692008959171172634206184380581278989999081666391528267108503"
    "9813609522242829719587993249808317734238106660385861768230295679126590"
    "8390972444782203928717828427457583267560097495187522617809715033399571"
    "0124142927808606451916188467080375525692807503004072582957175996256741"
    "6958199028585508053574180142683126826804771118716296486230523760774389"
    "7157494791542352379311268259974895147341335235499016003307513390038990"
    "1582196141853936279863966997543171337135092681583084518153432642302837"
    "0436056697857918994988629688023563560002153140124962200937852164145182"
    "1610847931627295268929335901602846813690082539801509776517015975714046"
    "5455848263618069464889478247144935435822126939965077545376582476552939"
    "5288811662441509565199205733657279155210616750060391443188845224391244"
    "5982465119470715706942563826139640100216780957119233780885476576542097"
    "8318327126238727841787217270826207296485682133095572761510633060271315"
    "2230040271215";

  BigInt dh_p =
    "2773513095749167337576358874942831569385761553923082020361322269992944"
    "8489006798120232791463013505228500900024049333039459029366992215417394"
    "0703109337560451078293297821188778260938274928421790028940882569457077"
    "8270715497001472804773372159699487464437256876108641279314813575799288"
    "0353560828726390302647822163531592190925834713707675874151479095828997"
    "9709275760692869280803757520668776451222054720062078905947201506921948"
    "2248258148634825249349597280042484353178956233483223727571140311838306"
    "9497997993896536595853659564600179648675284862073335665278820295284039"
    "2441154268228992660874384047813295938635270043470524847835602162062324"
    "6182957756186469188241103927864116660349640671385022766484753851141361"
    "3324705366794734356249759513986782234719409680441184269264165474240174"
    "7019497972779105025866714266206768504640255640079527841905839126323963"
    "3600041551667467165519541808705130094613958692430907777974227738480151"
    "9284479867895217795687886082284763600753200413473134257852188910038101"
    "0022934537091672256327978299054218233790927484338926431601990283936699"
    "4034965244475466733634646851920984543901636177633543005383561910647171"
    "8158178526713140623881625988429186051133467385983636059069118372099145"
    "33050012879383";

  Database::init();

  BigInt db = BigInt::rand_n_bits(4096, ms_since_epoch());

  Being bob("bob", rsa_p, rsa_q, rsa_e, dh_p, dh_g, db);

  BigInt sb = BigInt::rand_n_bits(256, ms_since_epoch());
  BigInt Db = bob.dh_pk;

  // Initialize the TCP server.
  try {
    TCPServer server(port);
    LOG("Server started on port: " << port);

    // Receive packet 1.
    JSON m1;
    server.recv_request(m1);
    LOG("Received packet 1");

    BigInt m1c = BigInt::from_base64(m1["payload"].get<std::string>());
    BigInt ses1 = BigInt::from_base64(m1["sess_key"].get<std::string>());

    BigInt m1a_bigint = bob.decrypt(ses1);

    JSON m1a = JSON::parse(BigInt::to_string(m1a_bigint));

    BigInt sa = BigInt::from_base64(m1a["key"].get<std::string>());
    u64 tod = BigInt::to_uint64(BigInt::from_base64(m1a["tod"].get<std::string>()));

    std::vector<u8> ct2 = BigInt::to_bytes(m1c);
    std::vector<u8> pt2(ct2.size());
    std::vector<u8> key_sa = BigInt::to_bytes(sa);

    ctr_decrypt(tod, key_sa.data(), ct2.data(), pt2.data(), ct2.size());

    BigInt something2_bigint = BigInt::from_bytes(pt2);
    JSON something2 = JSON::parse(BigInt::to_string(something2_bigint));

    JSON m1b = something2["agreement_data"].get<JSON>();
    BigInt sig1 = BigInt::from_base64(something2["signature"].get<std::string>());

    BigInt m1b_bigint = BigInt::from_string(m1b.dump());

    std::vector<u8> m1b_data = BigInt::to_bytes(m1b_bigint);
    std::vector<u8> hm1b_data;

    SHA3::absorb(m1b_data);
    SHA3::squeeze(hm1b_data);

    BigInt hm1b = BigInt::from_bytes(hm1b_data);

    bool verified = false;
    Being other;

    for (const auto& being : beings) {
      if (bob.verify(being, sig1) == hm1b) {
        other = Being(being.name, being.rsa_n, being.rsa_e);
        verified = true;
        break;
      }
    }

    CHECK(verified, "Error: unknown being.");

    BigInt h = BigInt::from_base64(m1b["hash_sess_key"].get<std::string>());
    BigInt Da = BigInt::from_base64(m1b["diffie_pub_k"].get<std::string>());

    std::vector<u8> m1a_data = BigInt::to_bytes(m1a_bigint);
    std::vector<u8> hm1a_data;

    SHA3::absorb(m1a_data);
    SHA3::squeeze(hm1a_data);

    BigInt hm1a = BigInt::from_bytes(hm1a_data);

    CHECK(h == hm1a, "Error: bad packet.");

    JSON m2a = {
      { "key", BigInt::to_base64(sb) }
    };

    BigInt m2a_bigint = BigInt::from_string(m2a.dump());

    BigInt ses2 = bob.encrypt(other, m2a_bigint);

    std::vector<u8> m2a_data = BigInt::to_bytes(m2a_bigint);
    std::vector<u8> hm2a_data;

    SHA3::absorb(m2a_data);
    SHA3::squeeze(hm2a_data);

    BigInt hm2a = BigInt::from_bytes(hm2a_data);

    JSON m2b = {
      { "hash_sess_key", BigInt::to_base64(hm2a) },
      { "diffie_pub_k", BigInt::to_base64(Db) }
    };

    BigInt m2b_bigint = BigInt::from_string(m2b.dump());

    std::vector<u8> m2b_data = BigInt::to_bytes(m2b_bigint);
    std::vector<u8> hm2b_data;

    SHA3::absorb(m2b_data);
    SHA3::squeeze(hm2b_data);

    BigInt hm2b = BigInt::from_bytes(hm2b_data);

    BigInt sig2 = bob.sign(hm2b);

    JSON m2c_json = {
      { "agreement_data", m2b },
      { "signature", BigInt::to_base64(sig2) }
    };

    BigInt m2c_bigint = BigInt::from_string(m2c_json.dump());

    std::vector<u8> pt1 = BigInt::to_bytes(m2c_bigint);
    std::vector<u8> ct1(pt1.size());
    std::vector<u8> key_sb = BigInt::to_bytes(sb);

    ctr_encrypt(tod, key_sb.data(), pt1.data(), ct1.data(), pt1.size());

    BigInt m2c = BigInt::from_bytes(ct1);

    JSON m2 = {
      { "payload", BigInt::to_base64(m2c) },
      { "sess_key", BigInt::to_base64(ses2) }
    };

    server.send_response(m2);
    LOG("Sent packet 2 to: " << other.name);

    BigInt Dab = Da.powm(db, dh_p);
    std::vector<u8> Dab1_hash;
    std::vector<u8> Dab1_data = BigInt::to_bytes(Dab);
    Dab1_data.insert(Dab1_data.begin(), static_cast<u8>(0x01));

    SHA3::absorb(Dab1_data);
    SHA3::squeeze(Dab1_hash);

    std::vector<u8> Dab2_hash;
    std::vector<u8> Dab2_data = BigInt::to_bytes(Dab);
    Dab2_data.insert(Dab2_data.begin(), static_cast<u8>(0x02));

    SHA3::absorb(Dab2_data);
    SHA3::squeeze(Dab2_hash);

    BigInt k1 = BigInt::from_bytes(Dab1_hash);
    BigInt k2 = BigInt::from_bytes(Dab2_hash);

    JSON m3;
    server.recv_hmac(m3);
    LOG("Received packet 3 from: " << other.name);

    BigInt m3_tag = BigInt::from_base64(m3["tag"].get<std::string>());

    server.recv_audio("audio_server.encrypted");
    LOG("Received audio from: " << other.name);

    struct stat statbuf;
    stat("audio_server.encrypted", &statbuf);

    std::ifstream audiofile("audio_server.encrypted", std::ios::binary);
    CHECK(audiofile, "Failed to open audio file.");

    std::vector<u8> audio(statbuf.st_size);
    audiofile.read((char *)audio.data(), statbuf.st_size);

    std::vector<u8> tag_hash;
    std::vector<u8> tag_data = BigInt::to_bytes(k2);
    tag_data.insert(tag_data.end(), audio.begin(), audio.end());

    SHA3::absorb(tag_data);
    SHA3::squeeze(tag_hash);

    BigInt tag = BigInt::from_bytes(tag_hash);

    CHECK(tag == m3_tag, "Error: bad tag.");

    decrypt_audio(k1, tod, "audio_server.encrypted", "audio_server.wav");

    play_audio("audio_server.wav");

    remove("audio_server.encrypted");
    remove("audio_server.wav");
  } catch (TCPSocketException& err) {
    std::cerr << "Server error: " << err.what() << std::endl;
  }

  return 0;
}
