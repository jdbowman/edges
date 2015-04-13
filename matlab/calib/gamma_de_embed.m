function R = gamma_de_embed(S11, S12S21, S22, Rp)


R = (Rp - S11)./(S22.*(Rp-S11) + S12S21);

