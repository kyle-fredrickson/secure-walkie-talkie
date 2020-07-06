import sys

sys.path.append('../src/')
import ECDHKE as ecdh

"""
NIST P521
p = 68647976601306097149819007990813932172694353001433054093944634591855431833976560521225596406614545549772963113914
80858037121987999716643812574028291115057151
a = 68647976601306097149819007990813932172694353001433054093944634591855431833976560521225596406614545549772963113914
80858037121987999716643812574028291115057148
b = 10938490380737342745111123907668055699362075989516837489945863944959531161507350160137087375737596232485921322967
06313309438452531591012912142327488478985984
x = 26617408020502170632287687167233609607298591687569731477066713684188029449964278084915450806277719023520942412250
65558662157113545570916814161637315895999846
y = 37571800257700204635455072244911836035944551347697624866945677796155444774405563166912344050129455395621444445372
89428522585666729196580810124344277578376784
"""

def main():
    p = 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151
    a = 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057148
    b = 1093849038073734274511112390766805569936207598951683748994586394495953116150735016013708737573759623248592132296706313309438452531591012912142327488478985984
    x = 2661740802050217063228768716723360960729859168756973147706671368418802944996427808491545080627771902352094241225065558662157113545570916814161637315895999846
    y = 3757180025770020463545507224491183603594455134769762486694567779615544477440556316691234405012945539562144444537289428522585666729196580810124344277578376784
    g = (x, y)

    ec1 = ecdh.ECDHKE(a, b, p, g)
    ec2 = ecdh.ECDHKE(a, b, p, g)
    print("Constructor passed:", ec1 != None and ec2 != None)

    ss1 = ec1.get_shared_secret(ec2.X)
    ss2 = ec2.get_shared_secret(ec1.X)

    print("Key Exchange passed:", ss1 == ss2)

if __name__ == "__main__":
    main()