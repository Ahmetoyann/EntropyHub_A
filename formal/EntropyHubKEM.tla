------------------------------- MODULE EntropyHubKEM -------------------------------
EXTENDS Naturals, Sequences

CONSTANTS PublicKeys, Ciphertexts, SharedSecrets

VARIABLES pk, sk, ct, ssEnc, ssDec

TypeInvariant ==
    /\ pk \in PublicKeys
    /\ sk \in PublicKeys
    /\ ct \in Ciphertexts
    /\ ssEnc \in SharedSecrets
    /\ ssDec \in SharedSecrets

Init ==
    /\ pk \in PublicKeys
    /\ sk = pk
    /\ ct \in Ciphertexts
    /\ ssEnc \in SharedSecrets
    /\ ssDec \in SharedSecrets

Encapsulate ==
    /\ ssEnc' \in SharedSecrets
    /\ UNCHANGED <<pk, sk, ct, ssDec>>

Decapsulate ==
    /\ ssDec' = ssEnc
    /\ UNCHANGED <<pk, sk, ct, ssEnc>>

Next == Encapsulate \/ Decapsulate

SharedSecretAgreement == ssEnc = ssDec

Spec == Init /\ [][Next]_<<pk, sk, ct, ssEnc, ssDec>>

=============================================================================
