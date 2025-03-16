# Transaction Cost Modeling in Cryptocurrency Backtesting

### İşlem Maliyeti Modellemesi

Kripto para birimi alım satım stratejileri için geriye dönük test metodolojilerinde işlem maliyetlerinin modellenmesi, stratejilerin gerçek dünya performansını doğru bir şekilde değerlendirmek için kritik öneme sahiptir. İşlem maliyetleri, alım satım stratejilerinin karlılığını önemli ölçüde etkileyebilir ve bu nedenle geriye dönük test süreçlerinde dikkate alınmalıdır.

**Lineer İşlem Maliyetleri:**

Lineer işlem maliyetleri, alım satım hacmiyle orantılı olarak artan maliyetlerdir. Bu tür maliyetler, şu şekilde modellenebilir: 1Tu= 0 kısıtlaması yerine 1Tu+κTbuyu++κTsellu−= 0 denklemi kullanılır (Author, Year). Burada κsell satış işlem maliyet oranları vektörünü, κbuy ise alış işlem maliyet oranları vektörünü temsil eder. u+ ve u− sırasıyla u'nun pozitif ve negatif kısımlarını ifade eder. −1Tut, satışlardan elde edilen toplam brüt gelir ile alımlar için ödenen toplam brüt tutar arasındaki farkı temsil eder ve bu fark, κTbuyu+ (alış işlemlerinin toplam işlem maliyeti) ve κTsellu− (satış işlemlerinin toplam işlem maliyeti) toplamına eşittir (Author, Year). İşlem maliyetlerinin varlığı, optimal politika hesaplamasını önemli ölçüde zorlaştırır (Author, Year).

**Dışbükey İşlem Maliyetleri ve Portföy Optimizasyonu:**

Model, riskten kaçınmayı, portföy kısıtlamalarını ve dışbükey işlem maliyetlerini dikkate alır (Author, Year). İşlem maliyetlerini göz ardı eden bir "maliyet körü" stratejisi, diğer buluşsal yöntemlerin performansını değerlendirmek için bir ölçüt olarak kabul edilir (Author, Year). "Tek adımlı" strateji, dinamik programlama yinelemesini, devam değerini işlem maliyetlerini göz ardı eden modelin değer fonksiyonu olarak alarak yaklaşık olarak değerlendirir; işlem maliyetleri yalnızca mevcut dönemde dikkate alınır (Author, Year). "Yuvarlanan al ve tut" stratejisi, her dönemde, sabit bir ufukta daha fazla ticaret fırsatı olmayacağı basitleştirici varsayımıyla işlem maliyetleriyle bir optimizasyon problemi çözer; ufkun sonundaki devam değeri yine işlem maliyetlerini göz ardı eden modelin değer fonksiyonu olarak alınır (Author, Year). İşlem maliyetleri ile portföy optimizasyonu, stokastik dinamik bir program olarak formüle edilir (Author, Year). İşlem maliyetleri olmadan, optimal yatırımlar tipik olarak yatırımcının servetine bağlıdır, ancak yatırımcının varlık pozisyonlarına bağlı değildir. Bununla birlikte, işlem maliyetleriyle, optimal yatırımlar yatırımcının ilk varlık pozisyonlarına bağlıdır ve durum uzayının boyutu, dikkate alınan varlıkların sayısı kadar büyüktür (Author, Year). Çözümler, işlem maliyetlerinin olmamasına büyük ölçüde dayanır. Uygulamada, işlemler maliyetlidir ve sürekli yeniden dengeleme oldukça pahalı olabilir (Author, Year). Sürekli yeniden dengeleme, işlem maliyetleri nedeniyle pahalı olabilir (Author, Year). Model, öngörülebilir getirileri ve dışbükey işlem maliyetlerini dikkate alır (Author, Year). Buluşsal yöntemler, optimal bir ticaret stratejisiyle performansta üst sınırlar ile tamamlanır (Author, Year). Sınırlar, gelecekteki getiriler hakkında mükemmel bilgiye sahip olan ancak bu ön bilgiyi kullandığı için cezalandırılan bir yatırımcıyı dikkate alarak verilir (Author, Year). Hem buluşsal yöntemler hem de ikili sınırlar Monte Carlo simülasyonu kullanılarak eşzamanlı olarak değerlendirilebilir (Author, Year). Buluşsal yöntemler ve ikili sınırlar, farklı fayda fonksiyonları, farklı işlem maliyeti biçimleri (dışbükey olmaları koşuluyla), farklı portföy kısıtlamaları ve farklı getiri modelleriyle ilgili sorunlara uyarlanabilir (Author, Year).

**Yürütme Zamanlaması ve İşlem Maliyetleri:**

İşlem maliyetlerinin değerlendirilmesinde yürütme zamanlamasının önemi vurgulanmaktadır (Author, Year). Hızlı yürütülen emirler daha yüksek maliyetlere yol açarken, daha kademeli işlemler varlığın değerinin daha uzun sürelerde değişebileceği için daha yüksek risk taşır (Author, Year). Farklı emir yürütme yaklaşımlarıyla ilişkili beklenen maliyeti ve riski ölçmek ve modellemek için bir veri seti kullanılır (Author, Year). İşlem maliyeti ölçüsü, emir gönderildiği andaki fiyatı bir kıyaslama fiyatı olarak alır (Author, Year). İşlem maliyeti, işlem fiyatı ile kıyaslama fiyatı arasındaki farkın ağırlıklı toplamıdır; ağırlıklar ise işlem gören miktarlardır (Author, Year). İşlem maliyetinin hem ortalaması hem de varyansı oluşturulur (Author, Year). İşlem maliyeti, yerel etkileri yakalayan geleneksel işlem maliyeti ölçüleriyle yakından ilişkili olan iki bileşene ayrılabilir (Author, Year). Yüksek beklenen maliyet ve düşük risk ile düşük beklenen maliyet ve yüksek risk arasında bir denge vardır (Author, Year). Piyasa koşulları ve emrin özelliklerine bağlı olarak değişen bir risk/maliyet dengesi sunulmaktadır (Author, Year). Veriler, emir gönderilme zamanı ile emri doldururken yapılan işlemlerin zamanları, fiyatları ve miktarları hakkında bilgiler içermektedir (Author, Year).

**Orantılı İşlem Maliyetleri ve Koşullu Talep Hedging:**

Orantılı işlem maliyetleri altında sürekli zamanlı bir modelde, herhangi bir koşullu talebi hedge etmek için gereken minimum başlangıç serveti için bir formül türetilmektedir (Author, Year). Ayrıca, terminal servetten elde edilen faydayı maksimize etme portföy optimizasyon probleminin optimal çözümünün varlığı kanıtlanmaktadır (Author, Year). Model, banka hesabı ve hisse senedi olmak üzere iki varlık içermektedir ve işlem maliyetleri, bankadan hisse senedine veya tersi yönde yapılan transferler için orantılıdır (Author, Year). Bir ticaret stratejisi, bu transferleri temsil eden uyarlanmış süreçler çiftidir (Author, Year). Bir koşullu talep, terminal zamanda banka hesabındaki ve hisse senedindeki hedef pozisyonlardır (Author, Year). Bir ticaret stratejisi, başlangıç pozisyonlarıyla başlayarak, terminal zamanda bu hedef pozisyonları karşılayacak kadar varlık sağlaması durumunda talebi hedge eder (Author, Year).


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
