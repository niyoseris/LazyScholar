# Applying Deep Learning for Cryptocurrency Price Prediction

### Kripto Para Fiyat Tahmininde Derin Öğrenme Uygulamaları

Kripto para birimleri, özellikle Bitcoin'in 2017'deki fiyat artışıyla birlikte popülerlik kazanması, yatırım stratejileri geliştirmek için yüksek frekanslı fiyat tahminlerini önemli hale getirmiştir. Bu bağlamda, derin öğrenme algoritmaları, Bitcoin fiyat tahmininde umut vadeden sonuçlar sunmaktadır. Bu bölümde, derin öğrenme yöntemlerinin kripto para fiyat tahminindeki uygulamaları ve mevcut araştırmalar incelenecektir.

**Derin Öğrenme Algoritmaları ve Bitcoin Fiyat Tahmini**

Bitcoin'in yüksek frekanslı trend tahmininde derin öğrenme algoritmalarının etkinliği çeşitli çalışmalarda test edilmiştir. Ji et al. (tarih belirtilmemiş), Bitcoin getirilerini tahmin etmek için Derin Sinir Ağları (DNN), Uzun Kısa Süreli Bellek (LSTM), Evrişimsel Sinir Ağları (CNN) ve Tekrarlayan Sinir Ağları (RNN) gibi derin öğrenme algoritmalarını kullanmışlardır. Ancak, bu çalışmada algoritmalar arasında önemli bir performans farkı bulunamamıştır. Alonso-Monsalve et al. (tarih belirtilmemiş) ise, dakika seviyesindeki Bitcoin fiyatlarından hesaplanan 18 teknik göstergeyi kullanarak CNN, hibrit CNN-LSTM ağı, Çok Katmanlı Algılayıcı (MLP) ve Radyal Tabanlı Fonksiyon (RBF) sinir ağlarını Bitcoin, Dash, Ether, Litecoin, Monero ve Ripple gibi altı popüler kripto para biriminin fiyat değişikliklerini tahmin etmek için kullanmışlardır. Bu çalışmada, hibrit CNN-LSTM ağının en iyi performansı gösterdiği ve Monero ve Dash'in fiyat değişikliklerini tahmin etmede %80 ve %74'e varan test doğruluklarına ulaştığı belirtilmiştir.

**CNN-LSTM Hibrit Modelinin Uygulanması**

Bu alandaki bir çalışma, Bitcoin fiyatlarının tek adımlı yüksek frekanslı trend tahminlerini gerçekleştirmek için CNN ve LSTM ağlarının derin öğrenme tekniklerini sınıflandırma algoritmaları olarak kullanmıştır (yazar belirtilmemiş, tarih belirtilmemiş). Model, Binance borsasında işlem gören Bitcoin'lerin dakika seviyesindeki fiyat değişikliklerini tahmin etmeyi ve varlıkları pasif olarak tutma stratejisinden daha iyi performans gösterebilen yatırım stratejileri oluşturmayı amaçlamaktadır. Modelin girdileri, dakika seviyesindeki açılış, kapanış, yüksek ve düşük fiyatlar ile işlem hacmidir.

Modelin mimarisi, bitişik veriler arasındaki ilişkilerden yararlanma ve yüksek frekanslı verinin işlenmesini hızlandırma yeteneği nedeniyle CNN'yi içermektedir. LSTM ağları ise, teknik göstergelerin zaman serisi verileri olan Bitcoin verileri arasındaki sıralı ilişkileri kullanmak için kullanılmaktadır. CNN katmanlarının çıktılarını girdi olarak alan iki derin LSTM katmanı, önceden oluşturulmuş CNN mimarisine eklenmiştir.

**Veri Seti ve Model Yapılandırması**

Çalışmada, 8 Temmuz 2020'den 11 Şubat 2021'e kadar olan dakika seviyesindeki Bitcoin fiyatları ve hacimleri toplanarak 313.327 veri noktası oluşturulmuştur. Fiyat değişikliği etiketleri (0 ve 1), sırasıyla fiyattaki düşüşü ve artışı belirtmektedir. Veri kümesinin %80'i eğitim seti olarak kullanılırken, geri kalanı geliştirme ve test setlerine bölünmüştür. Girdiler, 30 teknik göstergeyi hesaplamak için kullanılmıştır. CNN katmanları 40x30 boyutunda girdi almakta ve filtrelerden geçtikten sonra 28x10 boyutunda çıktı döndürmektedir. LSTM mimarisi ise, 2 katmanlı derin bir yapıya sahip olup, her katmanın çıktı birimi 100'dür.

**Diğer Yaklaşımlar ve Gelecek Çalışmalar**

Kripto para fiyat tahmininde RNN modellerinin uygulanmasını araştıran bir başka çalışmada, Basit RNN, LSTM ve GRU modelleri karşılaştırılmış ve Google Trendleri verilerinin eklenmesinin tahmin doğruluğunu artırıp artırmadığı incelenmiştir (yazar belirtilmemiş, tarih belirtilmemiş). Sonuçlar, test edilen RNN modelleri arasında önemli bir performans farkı olmadığını ve Google Trendleri verilerinin eklenmesinin modelin tahmin doğruluğunu önemli ölçüde artırmadığını göstermiştir.

Gelecekteki çalışmalarda, kayan pencere çapraz doğrulamasının uygulanması ve ek özellikler kullanılarak CNN ve CNN-LSTM hibrit modelinin yeniden kalibre edilmesi ve geliştirilmesi planlanmaktadır (yazar belirtilmemiş, tarih belirtilmemiş).

**Sonuç**

Derin öğrenme algoritmaları, kripto para fiyat tahmininde umut vadeden sonuçlar sunmaktadır. Özellikle CNN ve LSTM tabanlı hibrit modeller, yüksek frekanslı veriyi analiz etme ve zaman serisi ilişkilerini yakalama yetenekleri sayesinde etkili sonuçlar vermektedir. Ancak, farklı algoritmaların ve veri kaynaklarının kombinasyonlarının araştırılması ve modellerin sürekli olarak güncellenmesi, daha doğru ve güvenilir tahminler elde etmek için önemlidir.


## References

1. 251.pdf
2. 252.pdf
3. 253.pdf
4. 254.pdf
5. 255.pdf
6. 256.pdf
7. 257.pdf
8. 258.pdf
