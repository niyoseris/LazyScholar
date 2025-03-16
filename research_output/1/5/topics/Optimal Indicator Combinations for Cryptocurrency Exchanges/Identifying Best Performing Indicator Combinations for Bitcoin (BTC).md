# Identifying Best Performing Indicator Combinations for Bitcoin (BTC)

### Bitcoin (BTC) İçin En İyi Performans Gösteren Gösterge Kombinasyonlarının Belirlenmesi

Kripto para birimleri, özellikle Bitcoin, son yıllarda önemli bir ilgi görmüştür. Bu bağlamda, araştırmalar Bitcoin fiyatlarının yüksek frekanslı trend tahminlerine odaklanmıştır. Bu amaçla, evrişimsel sinir ağları (CNN) ve uzun kısa süreli bellek (LSTM) ağları gibi derin öğrenme teknikleri, dakika seviyesindeki teknik göstergeler kullanılarak uygulanmıştır. Bu yaklaşımlar, Bitcoin'leri pasif olarak elde tutma stratejisine kıyasla daha iyi performans gösteren ticaret stratejileri oluşturma potansiyeli sunmaktadır (Ji, Kim & Im, Tarih Belirtilmemiş).

Alonso-Monsalve ve diğerleri (Tarih Belirtilmemiş), dakika seviyesindeki Bitcoin fiyatlarından hesaplanan 18 teknik gösterge kullanarak, Bitcoin, Dash, Ether, Litecoin, Monero ve Ripple gibi popüler kripto para birimlerinin fiyat değişikliklerini tahmin etmek için CNN, hibrit CNN-LSTM ağı, MLP ve RBF sinir ağlarını kullanmışlardır. Hibrit CNN-LSTM ağının en iyi performansı gösterdiği ve Monero ve Dash'ın fiyat değişikliklerini tahmin etmede %80 ve %74'e varan test doğruluğuna ulaştığı sonucuna varmışlardır. Benzer şekilde, mevcut çalışmalarda da hibrit CNN-LSTM modelleri geliştirilmiş ve teknik göstergelerden yararlı sinyaller çıkarabildiği gösterilmiştir.

Bu modellerde kullanılan girdiler, Alonso-Monsalve ve diğerlerinin (Tarih Belirtilmemiş) çalışmalarına benzer şekilde, bazı eklemelerle birlikte 30 teknik göstergeyi içermektedir. Bu göstergeler arasında MOM, MOM ret, SMA ret, WMA ret, RSI, SK, SD10, LWR, CCI, MACD, ADOSC Binance ve ADOSC all bulunmaktadır. Teknik göstergelerin hesaplanması, momentum, son fiyat seviyeleri arasındaki ilişkiler, aşırı alım ve aşırı satım koşulları ve genel birikim ve dağılım dahil olmak üzere fiyat dinamiklerinin yararlı özelliklerini çıkaran bir transfer öğrenme süreci olarak görülebilir.

Model mimarisi, CNN ve LSTM olmak üzere iki ana bileşenden oluşmaktadır. CNN, bitişik veriler arasındaki ilişkileri kullanma ve yüksek frekanslı verilerin işlenmesini hızlandırma yeteneği nedeniyle tercih edilmiştir. LSTM ağları ise, Bitcoin verileri arasındaki sıralı ilişkileri daha iyi kullanmak amacıyla entegre edilmiştir.


## References

1. 185.pdf
2. 186.pdf
3. 187.pdf
4. 188.pdf
5. 189.pdf
6. 190.pdf
7. 191.pdf
8. 192.pdf
9. 193.pdf
10. 194.pdf
