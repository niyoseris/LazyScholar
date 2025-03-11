# Propensity Score Matching for Confounding Control

### Aşı-Ölüm İlişkilerini Analiz Etmede Eğilim Skoru Eşleştirmesi ile Karıştırıcı Değişkenlerin Kontrolü

Aşı-ölüm ilişkilerini analiz ederken, gözlemsel çalışmalarda karıştırıcı değişkenlerin (confounding) kontrolü kritik öneme sahiptir. Randomize kontrollü çalışmalar (RCT'ler) altın standart olarak kabul edilse de, her zaman etik veya pratik olmayabilirler (Rosenbaum & Rubin, 1983). Bu tür durumlarda, eğilim skoru eşleştirmesi (propensity score matching - PSM), karıştırıcı değişkenlerin etkisini azaltmak için yaygın olarak kullanılan bir istatistiksel yöntemdir (Rosenbaum & Rubin, 1983).

Eğilim skoru, bir bireyin belirli bir tedavi veya aşıyı alma olasılığının tahminidir (P(T=1)) (Rosenbaum & Rubin, 1983). Bu skor, genellikle, tedaviye seçilme olasılığını etkilediği düşünülen bir dizi gözlemlenebilir değişkenin (X) kullanıldığı bir lojistik regresyon modeli ile elde edilir (Rosenbaum & Rubin, 1983). Eğilim skoru eşleştirmesi, aşılanan ve aşılanmayan bireyler arasında benzer eğilim skorlarına sahip olanları eşleştirerek, tedavi grupları arasındaki karşılaştırılabilirliği artırmayı hedefler (Rosenbaum & Rubin, 1983). Bu sayede, aşı ve ölüm arasındaki ilişki daha doğru bir şekilde değerlendirilebilir ve nedensel çıkarımlar yapılması kolaylaşır.

Eşleştirme işlemi, farklı yöntemlerle gerçekleştirilebilir. Bire bir eşleştirmede (one-to-one matching), tedavi gören birim, eğilim skoru açısından en yakın olan tedavi görmeyen birimle eşleştirilir (Rosenbaum & Rubin, 1983). Çekirdek tabanlı eşleştirmede (kernel-based matching) ise, tedavi gören birimin sonucu, tedavi görmeyen tüm birimlerin sonuçlarının ağırlıklı ortalaması olarak hesaplanır; ağırlıklar, eğilim skorları arasındaki yakınlığa bağlıdır (Rosenbaum & Rubin, 1983). Mahalanobis metrik eşleştirmesi gibi daha gelişmiş eşleştirme teknikleri de mevcuttur (Rosenbaum & Rubin, 1983).

Eğilim skoru analizinin uygulanması çeşitli adımları içerir: (1) tedavi ve sonuç değişkenlerinin belirlenmesi, (2) tedavi değişkenini ve sonucu tahmin eden değişkenlerin belirlenmesi, (3) eğilim skorlarının tahmin edilmesi, (4) tedavi ve kontrol gruplarının kovariatların ortalamaları ve varyansları açısından dengeli olup olmadığının değerlendirilmesi (Rosenbaum & Rubin, 1983). Eğilim skoru hesaplanırken, hem bağımsız değişkeni hem de sonuç değişkenini tahmin eden kovariatlar dahil edilmelidir (Rosenbaum & Rubin, 1983).

Eşleştirme sonrasında, tedavi ve kontrol grupları arasındaki denklik, eğilim skorlarının ortalamalarındaki farkın 0,5 standart sapmadan küçük olması, eğilim skorlarının varyanslarının oranının bire yakın olması ve kovariatların artıklarının varyanslarının oranının eğilim skoru için ayarlandıktan sonra bire yakın olması koşullarıyla değerlendirilir (Rosenbaum & Rubin, 1983).

Eğilim skoru eşleştirmesinin yanı sıra, ters olasılık ağırlıklandırması (inverse probability weighting - IPW) gibi alternatif yöntemler de karıştırıcı değişkenleri kontrol etmek için kullanılabilir (Rosenbaum & Rubin, 1983). IPW'de, tedavi edilen bireyler için ağırlık w(x)=1/p(x) ve tedavi edilmeyen bireyler için ağırlık w(x)=1/(1 -p(x)) olarak hesaplanır (Rosenbaum & Rubin, 1983).

Sonuç olarak, eğilim skoru eşleştirmesi, aşı-ölüm ilişkilerini analiz ederken karıştırıcı değişkenleri kontrol etmek için güçlü bir araçtır. Bu yöntem, gözlemsel çalışmalarda nedensel çıkarımlar yapmayı kolaylaştırır ve aşıların etkinliği ve güvenliği hakkında daha doğru sonuçlar elde edilmesine yardımcı olur. STATA ve R gibi istatistiksel yazılım paketleri, eğilim skoru eşleştirme ve diğer ilgili analizlerin uygulanmasını kolaylaştırmaktadır (Rosenbaum & Rubin, 1983).


## References

1. 175.pdf
2. 176.pdf
3. 177.pdf
4. 178.pdf
5. 179.pdf
6. 180.pdf
7. 181.pdf
8. 182.pdf
9. 183.pdf
10. 184.pdf
