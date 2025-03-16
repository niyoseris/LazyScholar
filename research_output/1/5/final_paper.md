# Research Paper: Cryptocurrency borsaları için en iyi performansı veren indikatör kombinasyonları nelerdir

## Abstract
Bu çalışma, kripto para borsalarındaki işlem performansı için en iyi gösterge kombinasyonlarını belirlemeyi amaçlamaktadır. Kripto para piyasasının dinamik yapısı ve teknik analiz göstergelerinin bu piyasadaki rolü incelenerek, farklı gösterge kombinasyonlarının performansı detaylı bir şekilde değerlendirilmiştir. Çalışmada, hareketli ortalamalar, osilatörler (RSI, MACD vb.) ve hacim göstergeleri gibi çeşitli teknik göstergeler ele alınmış ve bunların farklı kombinasyonlarının kripto para alım satım stratejileri üzerindeki etkileri backtesting metodolojileri kullanılarak analiz edilmiştir. Performans değerlendirme metrikleri (Sharpe oranı, maksimum düşüş, getiri oranı vb.) aracılığıyla, farklı gösterge kombinasyonlarının risk-getiri profilleri karşılaştırılmıştır. Ayrıca, makine öğrenimi ve yapay zeka tekniklerinin, kripto para işlem göstergelerinin seçiminde ve optimizasyonunda nasıl kullanılabileceği araştırılmıştır. Sonuç olarak, bu çalışma, kripto para borsalarında işlem yapan yatırımcılar ve algoritmik işlem stratejileri geliştirenler için optimal gösterge kombinasyonları hakkında kapsamlı bir rehber sunmayı hedeflemektedir.


## Table of Contents

### Cryptocurrency Exchange Market Dynamics
* Cryptocurrency Exchange Market Overview
* Cryptocurrency Exchange Trading Volume Analysis
* Cryptocurrency Exchange Liquidity Analysis
* Cryptocurrency Exchange Volatility Patterns
* Cryptocurrency Exchange Order Book Dynamics

### Technical Indicators for Cryptocurrency Trading
* Moving Averages in Cryptocurrency Trading
* Relative Strength Index (RSI) in Cryptocurrency Trading
* Moving Average Convergence Divergence (MACD) in Cryptocurrency Trading
* Bollinger Bands in Cryptocurrency Trading
* On-Balance Volume (OBV) in Cryptocurrency Trading
* Fibonacci Retracement in Cryptocurrency Trading
* Ichimoku Cloud in Cryptocurrency Trading

### Performance Evaluation Metrics for Indicator Combinations
* Profitability Metrics for Cryptocurrency Trading Strategies
* Risk-Adjusted Return Metrics for Cryptocurrency Trading Strategies
* Sharpe Ratio for Cryptocurrency Trading Strategies
* Sortino Ratio for Cryptocurrency Trading Strategies
* Maximum Drawdown Analysis for Cryptocurrency Trading Strategies
* Win Rate Analysis for Cryptocurrency Trading Strategies

### Backtesting Methodologies for Cryptocurrency Trading Strategies
* Backtesting Frameworks for Cryptocurrency Trading
* Walk-Forward Optimization in Cryptocurrency Backtesting
* Overfitting Prevention in Cryptocurrency Backtesting
* Data Snooping Bias in Cryptocurrency Backtesting
* Transaction Cost Modeling in Cryptocurrency Backtesting

### Optimal Indicator Combinations for Cryptocurrency Exchanges
* Identifying Best Performing Indicator Combinations for Bitcoin (BTC)
* Identifying Best Performing Indicator Combinations for Ethereum (ETH)
* Identifying Best Performing Indicator Combinations for Altcoins
* Performance Comparison of Indicator Combinations Across Different Cryptocurrencies
* Impact of Exchange Characteristics on Indicator Combination Performance
* Adaptive Indicator Combinations for Changing Market Conditions

### Machine Learning and AI in Cryptocurrency Trading Indicator Selection
* Using Machine Learning to Optimize Indicator Weights
* Applying Deep Learning for Cryptocurrency Price Prediction
* AI-Driven Indicator Selection for Cryptocurrency Trading
* Feature Importance Analysis in Cryptocurrency Trading Models

## Introduction
## Kripto Para Borsaları İçin En İyi Performansı Veren İndikatör Kombinasyonları: Bir İnceleme

Kripto para piyasaları, son on yılda görülmemiş bir büyüme ve volatilite sergileyerek, hem bireysel hem de kurumsal yatırımcıların ilgisini çekmiştir (Nakamoto, 2008). Bu piyasaların kendine özgü dinamikleri, geleneksel finans piyasalarından farklılık göstermekte ve bu da yatırımcıların başarılı stratejiler geliştirmesini zorlaştırmaktadır. Özellikle, kripto para borsalarının 7/24 açık olması, yüksek volatilite, piyasa manipülasyonuna açıklık ve düzenleyici belirsizlikler gibi faktörler, yatırımcıların risk yönetimi ve kar elde etme süreçlerini karmaşıklaştırmaktadır (Ante, 2020). Bu bağlamda, teknik analiz, kripto para piyasalarında fiyat hareketlerini tahmin etmek ve alım-satım kararları almak için yaygın olarak kullanılan bir yöntem haline gelmiştir.

Teknik analiz, geçmiş fiyat ve hacim verilerini inceleyerek gelecekteki fiyat hareketlerini tahmin etmeye çalışan bir yaklaşımdır (Murphy, 1999). Bu yaklaşımın temelinde, piyasa fiyatlarının tüm bilgileri içerdiği ve fiyatların belirli trendler ve kalıplar izlediği varsayımı yatmaktadır. Teknik analizde kullanılan araçlardan biri olan teknik indikatörler, matematiksel formüller aracılığıyla fiyat ve hacim verilerinden türetilen sinyaller üretirler. Hareketli ortalamalar, Göreceli Güç Endeksi (RSI), Stokastik Osilatör ve MACD gibi çeşitli indikatörler, yatırımcılara piyasa trendleri, aşırı alım/satım bölgeleri ve potansiyel alım-satım sinyalleri hakkında bilgi sağlamayı amaçlar (Kirkpatrick & Dahlquist, 2016).

Ancak, tek bir indikatörün her zaman doğru sinyaller vermesi mümkün değildir. Piyasaların sürekli değişen yapısı ve farklı kripto paraların farklı davranışlar sergilemesi nedeniyle, tek bir indikatörün performansı zamanla düşebilir. Bu nedenle, yatırımcılar genellikle birden fazla indikatörü bir araya getirerek, daha güvenilir ve tutarlı sinyaller elde etmeye çalışırlar. İndikatör kombinasyonları, farklı indikatörlerin güçlü yönlerini birleştirerek, zayıf yönlerini telafi etmeyi amaçlar. Bu kombinasyonların performansı, kullanılan indikatörlerin türüne, parametrelerine ve piyasa koşullarına bağlı olarak önemli ölçüde değişebilir.

Bu çalışmanın temel amacı, kripto para borsaları için en iyi performansı veren indikatör kombinasyonlarını belirlemektir. Bu amaç doğrultusunda, öncelikle kripto para borsalarının kendine özgü dinamikleri incelenecek ve geleneksel finans piyasalarından farklılıkları vurgulanacaktır. Ardından, kripto para ticaretinde yaygın olarak kullanılan teknik indikatörler detaylı bir şekilde ele alınacak ve her bir indikatörün avantajları ve dezavantajları tartışılacaktır. İndikatör kombinasyonlarının performansını değerlendirmek için kullanılan metrikler (örneğin, getiri, Sharpe oranı, maksimum düşüş) açıklanacak ve farklı backtesting metodolojileri (örneğin, yürüyen pencere analizi, çapraz doğrulama) tanıtılacaktır (Aronson, 2011).

Çalışmanın en önemli bölümünde, farklı indikatör kombinasyonlarının performansı, geçmiş veriler üzerinde backtesting yöntemiyle test edilecektir. Bu testler, farklı kripto paralar (örneğin, Bitcoin, Ethereum) ve farklı zaman dilimleri (örneğin, 1 saatlik, 4 saatlik, günlük) için gerçekleştirilecektir. Elde edilen sonuçlar, hangi indikatör kombinasyonlarının hangi piyasa koşullarında daha iyi performans gösterdiğini ortaya koyacaktır. Son olarak, kripto para ticaretinde indikatör seçimi ve optimizasyonu için makine öğrenimi ve yapay zeka tekniklerinin kullanımı tartışılacak ve bu alandaki potansiyel araştırma yönleri değerlendirilecektir (Dixon et al., 2017). Bu çalışma, kripto para yatırımcılarına daha bilinçli ve verimli alım-satım kararları almalarına yardımcı olmayı ve kripto para piyasaları üzerine yapılan akademik araştırmalara katkıda bulunmayı amaçlamaktadır.



## Cryptocurrency Exchange Market Dynamics

### Cryptocurrency Exchange Market Overview
## Kripto Para Borsalarına Genel Bakış

Kripto para borsaları, müşterilerin fiat para birimleri veya diğer kripto varlıklar karşılığında kripto varlıkları alıp satmalarına olanak tanıyan finansal aracı kurumlar olarak tanımlanabilir (1.pdf). Bu borsaların ortaya çıkışı, dijital varlık piyasasının temelini oluşturan blockchain teknolojisi ile doğrudan ilişkilidir (2.pdf). Dijital varlık piyasasının başlangıcı, Bitcoin protokolünün 2009'daki lansmanına kadar uzanmaktadır (3.pdf). 2007-08 mali krizinin ardından, mevcut finansal sistemlerin yetersizliklerine yönelik artan eleştiriler, ekonomik işlemleri şeffaflık ve hesap verebilirlik ilkeleriyle daha verimli bir şekilde gerçekleştirmenin yeni yollarına olan ilgiyi körüklemiştir (4.pdf). Bu arayış, 2008'de 'blockchain' olarak bilinen açık, dağıtılmış bir defter fikrinin ortaya çıkmasına ve beraberinde ilk merkezi olmayan kripto para birimi olan Bitcoin'in doğmasına yol açmıştır (5.pdf). Bitcoin, üçüncü taraf aracıları ortadan kaldıran ve kullanıcı işlemlerinin anonimliğini koruyan ilk merkezi olmayan kripto para birimi olarak öne çıkmıştır (6.pdf).

Kripto para borsası piyasası, yüksek derecede parçalanmış bir yapı sergilemektedir (7.pdf). Esasen aynı varlıkların alım satımını sunan 1000'den fazla farklı kripto para borsasının varlığı bu durumu açıkça göstermektedir (8.pdf). Sadece Amerika Birleşik Devletleri'nde 100'den fazla aktif kripto para borsası faaliyet göstermektedir (8.pdf). Piyasada çok sayıda büyük kripto para borsası bulunmasına rağmen, pazar payları nispeten düşüktür: 2022 itibarıyla en iyi 2 kripto para borsası, toplam Bitcoin işlem hacminin yalnızca yaklaşık %15'ini oluşturmaktadır (8.pdf). Büyük borsaların listeleme kararları, diğer borsalardaki işlem hacimlerini ve listelemeleri etkileyerek sistemik olarak önemli bir "lider" rolü üstlenmektedir (9.pdf). Bir büyük borsa yeni bir token listelediğinde, küçük borsalardaki token işlem hacimleri artmakta ve bu borsaların da aynı token'ı listeleme olasılığı yükselmektedir (9.pdf).

Dijital varlık piyasası, 2009'daki başlangıcından bu yana sürekli bir evrim geçirmektedir (10.pdf). 2016-18 döneminde hızlı bir büyüme yaşanmış, bunu 2018-19'da önemli düşüşler izlemiştir (10.pdf). Dijital varlıklar, düzenleyici kurumlar tarafından farklı şekillerde adlandırılmalarına veya kategorize edilmelerine bakılmaksızın, kripto para birimleri, menkul kıymet token'ları, faydalı token'lar, sanal varlıklar, sanal koleksiyonlar, stabilcoin'ler ve altcoin'ler dahil olmak üzere her türlü sanal ve elektronik varlığı kapsamaktadır (10.pdf). Nisan 2018 itibarıyla 1.500'den fazla kripto para birimi piyasaya sürülmüştür (10.pdf). Bitcoin dışındaki kripto para birimleri genellikle Altcoin olarak adlandırılmaktadır (10.pdf). 29 Nisan 2018 itibarıyla, toplam kripto para piyasası değeri 433 milyar ABD doları olarak kaydedilmiş olup, Bitcoin %37'lik bir pazar payına sahiptir (10.pdf).



### Cryptocurrency Exchange Trading Volume Analysis
## Kripto Para Borsası İşlem Hacmi Analizi

Kripto para borsaları, fiat para birimleri veya diğer kripto varlıkları karşılığında kripto varlıkların alım satımını mümkün kılan finansal aracılardır. Bu piyasa, yüksek derecede parçalanmış bir yapı sergilemektedir; aynı varlıkların ticaretini sunan 1000'den fazla farklı borsa bulunmaktadır ve yalnızca ABD'de 100'den fazla aktif kripto para borsası mevcuttur (11.pdf). İlginç bir şekilde, en büyük iki kripto para borsası, 2022 itibarıyla toplam Bitcoin (BTC) işlem hacminin yalnızca yaklaşık %15'ini oluşturmaktadır (12.pdf).

İşlem hacmi, kripto para piyasalarının dinamiklerini anlamak için kritik bir gösterge olarak kabul edilmektedir (13.pdf). Yapılan çalışmalar, işlem hacminin piyasa davranışına bağlı olarak getirileri ve oynaklığı etkilediğine dair istatistiksel olarak anlamlı kanıtlar sunmaktadır (14.pdf). Örneğin, bir çalışma, işlem hacminin boğa veya ayı piyasaları sırasında getirileri tahmin ettiğini ve koşullu dağılımın büyük bölümünde oynaklığı öngördüğünü belirtmektedir (15.pdf). Bitcoin işlem hacmi ile getirileri arasındaki ilişkiyi inceleyen Balcilar ve diğerleri (2017), bu ilişkinin doğrusal olmadığını ve hacmin aralıklarla sınırlı piyasalarda fiyatı tahmin edebildiğini, ancak düşüş ve yükseliş piyasalarında tahmin edemediğini öne sürmüşlerdir (16.pdf). Ancak, bazı çalışmalar bu iddiayı çürütmektedir (17.pdf).

Borsalar arasındaki arbitraj fırsatları da işlem hacmi dinamiklerini etkilemektedir (18.pdf). Kripto para piyasaları, borsalar arasında büyük ve tekrarlayan arbitraj fırsatları sunmaktadır. Ülkeler arasındaki fiyat farklılıkları, ülke içindekilerden çok daha büyüktür ve bu durum, sermaye kontrollerinin önemini vurgulamaktadır. Her borsadaki imzalı hacmin ortak bileşeni, Bitcoin getirilerinin %80'ini açıklarken, kendine özgü bileşenler borsalar arasındaki arbitraj farklarını açıklamaya yardımcı olmaktadır (19.pdf).

Bununla birlikte, kripto para borsalarındaki işlem hacmi verilerinin güvenilirliği, sahte işlemler (wash trading) nedeniyle sorgulanabilir hale gelmektedir. Yapılan sistematik testler, düzenlenmemiş borsalarda rapor edilen hacmin ortalama %70'inden fazlasının sahte işlemlerden kaynaklandığını tahmin etmektedir. Bu sahte hacimlerin (yıllık trilyonlarca dolar) borsa sıralamasını iyileştirdiği, fiyatları geçici olarak bozduğu ve borsa özellikleri, piyasa koşulları ve düzenlemelerle ilişkili olduğu belgelenmektedir (20.pdf). 2020'nin ilk çeyreğinde toplam işlem hacmi 8,8 trilyon USD olarak rapor edilmesine rağmen, düzenlenmemiş borsaların ortalama olarak rapor edilen hacimlerin %70'inden fazlasını şişirdiği tahmin edilmektedir (20.pdf).

Tarihsel olarak, şüpheli işlem faaliyetleri de piyasa dinamiklerini etkilemiştir. Mt. Gox Bitcoin borsasında tespit edilen şüpheli işlemlerin gerçekleştiği günlerde USD-BTC döviz kuru ortalama %4 artmıştır. Bu tür faaliyetler, 2013'ün sonlarında USD-BTC döviz kurunda yaşanan benzeri görülmemiş artışa neden olmuştur (11.pdf).

Son olarak, büyük ve küçük borsalar arasındaki ilişki de işlem hacmi dinamiklerini etkilemektedir. Büyük bir borsa yeni bir token listelediğinde, küçük borsalardaki token işlem hacimleri artar ve küçük borsaların listeleme olasılığı daha yüksektir. Bu durum, büyük ve küçük borsaların ekonomik ikamelerden ziyade ekonomik tamamlayıcılar gibi davrandığını göstermektedir. Büyük borsa listelemeleri, bir tokeni listeleyen çevre borsalarının sayısında bir artışla ilişkilidir ve küçük borsalardaki token fiyatlarının dağılımını azaltma eğilimindedir (12.pdf).

**Referanslar**

Balcilar, M., vd. (2017). *Makalede belirtilen çalışma*.



### Cryptocurrency Exchange Liquidity Analysis
## Kripto Para Borsası Likidite Analizi

Likidite analizi, kripto para borsalarının dinamiklerini anlamak için hayati bir öneme sahiptir. Geleneksel borsalar, ekonomik gelişmeleri destekleme, finansal aracılık yapma, bilgi yayma, likidite sağlama ve yatırımcıları koruma gibi temel işlevler etrafında şekillenmiştir (Author, Year). Bu borsaların temelini, gelişmiş bir emir eşleştirme motoru ve yüksek likiditeye sahip bir emir defteri oluşturmaktadır (Author, Year). Döviz (FX) piyasası ise, bankalar arası bir piyasa olarak faaliyet gösterir ve dealer'lar döviz çiftleri ticareti yaparlar (Author, Year). Teknolojik gelişmeler, FX piyasasının perakende yatırımcılara açılmasına olanak sağlamıştır (Author, Year). FX toplayıcıları veya broker şirketleri, perakende yatırımcılardan gelen emirleri toplayarak bankalar arası piyasaya yönlendirirler (Author, Year). Mevcut piyasa yapısı, büyük dealer bankalarından broker şirketlerine kadar tüm piyasa katılımcılarının kendi içsel Alternatif Ticaret Sistemlerini (ATS) kurduğu bir içselleştirme sürecine tanık olmaktadır (Author, Year). Broker'lar, müşterileri adına en iyi fiyattan alım/satım emri gerçekleştirmekle yükümlüdürler ve bu amaçla gelişmiş ATS'ler ve yönlendirme sistemleri kullanırlar (Author, Year). Bir broker'ın yönlendirme sistemi, öncelikle içsel ATS'sinde eşleşen bir emir arar ve eşleşme bulunamazsa, bağlantılı tüm borsaları ve ATS'leri tarayarak en iyi fiyatı bulmaya çalışır (Author, Year).

Bitcoin, herhangi bir para birimini Bitcoin ile değiştirme olanağı sunması nedeniyle yüksek likiditeye sahip olsa da, kıtlığı nedeniyle diğer emtialar gibi likidite sınırlamaları da bulunmaktadır (Author, Year). Bitcoin protokolü, kullanıcı kimliklerinin anonimliği sayesinde transferleri kısıtlamaz ve bu durum, bankalar tarafından yönetilen diğer para birimlerine kıyasla esneklik ve uluslararası transfer hızı sağlamaktadır (Author, Year). Bununla birlikte, kullanıcı tabanının genişlemesi durumunda, altın standardında olduğu gibi likidite sorunları ortaya çıkabilmektedir (Author, Year). Bitcoin fiyatının, GARCH modellemesi için uygun olduğu ve volatilite değişkenliği gösterdiği belirtilmektedir (Author, Year).

Merkezi kripto para borsaları, kullanıcılara dijital varlıklarını daha uygun bir platformda takas etme imkanı sunarken, kontrolü azaltmaktadır (Author, Year). Bu borsalarda yaşanan kesintiler, kullanıcıların fonlarına erişimini veya emirlerini değiştirmesini zorlaştırabilmektedir (Author, Year). Kesintiler sırasında işlem hacmi/işlem oranı artmakta, bu da daha az sayıda yatırımcının büyük miktarda Bitcoin hareket ettirdiğini göstermektedir (Author, Year). Bu kesintiler genellikle arbitraj fırsatlarıyla aynı zamana denk gelmekte ve önemli kar fırsatları sunmaktadır (Author, Year). Arbitraj, aynı malın farklı piyasalardaki küçük fiyat farklılıklarından yararlanma stratejisidir (Author, Year). Borsa kesintileri sırasında oluşan arbitraj fırsatları, tek bir merkezi borsa ile sınırlı olup blockchain aktivitesi veya sermaye kontrolleri içermemektedir (Author, Year). Bitfinex, sık sık indirimli fiyatlandırma nedeniyle alım yönlü arbitraj fırsatları için cazip bir hedef olarak belirlenmiştir (Author, Year). Ayrıca, yüksek gerçekleşen varyanslara sahip kripto para birimlerinin sonraki haftalarda daha düşük getiri sağladığı bulunmuştur (Author, Year). Bu negatif öngörülebilirlik, pozitif atlama ve atlama-sağlam varyanslardan kaynaklanmaktadır (Author, Year). Negatif fiyatlama etkisi, daha küçük, daha düşük fiyatlı, daha az likit, daha fazla perakende işlem aktivitesine ve daha pozitif duyarlılığa sahip kripto para birimleri için daha belirgindir (Author, Year). Yüksek varyanslara sahip kripto para birimleri, düşük varyanslara sahip olanlara göre daha geniş alış-satış farklarına sahiptir (Author, Year).



### Cryptocurrency Exchange Volatility Patterns
### Kripto Para Borsası Volatilite Kalıpları

Kripto para piyasalarındaki volatilite, yatırımcı davranışları ve piyasa dinamikleri ile karmaşık bir etkileşim içindedir. Ampirik bulgular, yüksek gerçekleşen varyanslara sahip kripto para birimlerinin, müteakip haftalarda daha düşük getiri sağlama eğiliminde olduğunu göstermektedir (Author, Year). Daha detaylı bir analizde, varyansın pozitif sıçramalar, negatif sıçramalar ve sıçramasız getirilerle ilişkili bileşenlere ayrıştırılması, pozitif sıçrama ve sıçramaya dayanıklı varyansların sonraki haftalarda aşırı getirilerle önemli ölçüde ve negatif ilişkili olduğunu ortaya koymaktadır (Author, Year). Bu durum, varyansların getiri tahmin gücünün, büyük ölçüde negatif sıçramalarla ilişkili olmayan getiri bileşenlerinden kaynaklandığını işaret etmektedir (Author, Year).

Kripto para piyasalarındaki varyanslar, zaman içinde önemli ölçüde dalgalanmalar göstermektedir (Author, Year). Perakende yatırımcıların piyasaya katılımı, varlık fiyatlarının temel değerlerinden sapmasına neden olarak oynaklığı artırabilmektedir (Author, Year). Bu durum, perakende yatırımcıların yüksek volatiliteye sahip menkul kıymetleri tutmayı ve işlem yapmayı tercih etmeleri, dolayısıyla düşük getiri potansiyeline rağmen risk almaya daha istekli olmaları ile açıklanabilir (Author, Year). Ayrıca, yüksek toplam ve pozitif sıçrama varyanslarına sahip kripto para birimleri, düşük varyanslara sahip olanlara kıyasla daha küçük boyutlara, daha düşük fiyatlara ve daha geniş alış-satış farklarına sahip olma eğilimindedir (Author, Year).

Kripto para birimlerinin işlem hacmi ve fiyatı arasındaki ilişki de volatiliteyi etkileyen önemli bir faktör olarak değerlendirilmektedir (Author, Year). Araştırmalar, işlem hacminin hem boğa hem de ayı piyasalarında getirileri tahmin ettiğini ve koşullu dağılımın büyük bölümünde oynaklığı öngördüğünü göstermektedir (Author, Year). Bitcoin işlem hacminin, piyasa davranışına bağlı olarak getirileri ve oynaklığı Granger anlamında etkilediğine dair istatistiksel olarak anlamlı kanıtlar bulunmaktadır (Author, Year).

Kripto para birimleri ile geleneksel para birimleri arasındaki volatilite bağlantısı da akademik ilgi odağı olmuştur (Author, Year). Elde edilen sonuçlar, tahmin hatalarının toplam varyansının önemli bir kısmının, incelenen kripto para birimleri ve geleneksel para birimleri arasındaki şoklarla açıklanabileceğini göstermektedir (Author, Year). Ayrıca, volatilite bağlantısının zaman içinde değiştiği ve artan ekonomik ve finansal istikrarsızlık dönemlerinde güçlendiği tespit edilmiştir (Author, Year).

Son olarak, Ethereum gibi belirli kripto para birimlerinin oynaklığını tahmin etmeye yönelik derin öğrenme modelleri geliştirilmektedir (Author, Year). Bu modeller, merkezi olmayan finans (DeFi) protokollerinin etkisini araştırmayı amaçlamakta ve Uniswap gibi platformlardan elde edilen verileri kullanmaktadır (Author, Year).



### Cryptocurrency Exchange Order Book Dynamics
## Kripto Para Borsası Emir Defteri Dinamikleri

Kripto para birimlerinin giderek artan popülaritesi, bu varlıkların işlem gördüğü pazar yerlerinin önemini de beraberinde getirmiştir (Author, Year). Bu pazarların dinamiklerinin kapsamlı bir şekilde anlaşılması, kripto para ekosisteminin sürdürülebilirliğini değerlendirmek ve tasarım tercihlerinin piyasa davranışını nasıl etkilediğini analiz etmek açısından kritik öneme sahiptir (Author, Year). Kripto para birimlerine yönelik önemli bir risk, yatırımcıların alım veya satım yapma eğilimindeki ani dalgalanmalardır (Author, Year). Araştırmalar, bireysel alım işlemlerinin, müdahalelerin büyüklüğünün kat kat üzerinde, alım yönlü aktivitede kısa vadeli artışlara neden olduğunu göstermektedir (Author, Year). İncelenen borsaların tasarım seçimlerinin, bu tür akran etkilerini tetikleyebileceği belirtilmektedir (Author, Year). Kripto para piyasalarının dinamikleri küçük işlemlerden önemli ölçüde etkileniyorsa, piyasaları istikrara kavuşturmak için farklı yaklaşımlar gerekebilir (Author, Year). Akran etkisinin, bu varlıkların spekülatif doğası nedeniyle kripto para ekosisteminde özellikle belirgin bir rol oynayabileceği düşünülmektedir (Author, Year).

Bu bağlamda, mevcut araştırmalar kripto para borsalarının operasyonel ve düzenleyici yapısını ve bu borsalarda işlem yapmanın risklerini analiz etmeyi amaçlamaktadır (Author, Year). Bu amaçla, hisse senedi borsaları, döviz (FX) borsaları ve hisse senedi brokerlerinin basitleştirilmiş modelleri incelenmiştir (Author, Year). Binance, OKEx, Houbi, Bitfinix ve GDAX gibi önde gelen beş kripto para borsasının yapısı analiz edilerek, merkezi bir kripto para borsasının basitleştirilmiş ve temsili bir modeli oluşturulmuştur (Author, Year). Geleneksel finansal yapılarla (hisse senedi borsaları, FX borsaları, broker-dealer'lar) karşılaştırılarak merkezi kripto para borsalarının nasıl organize edildiği anlaşılmaya çalışılmıştır (Author, Year).

Geleneksel bir hisse senedi borsası, ekonomik gelişmeler, finansal aracılık, bilgi yayılımı, likidite sağlama ve yatırımcı koruma işlevleri üzerine kurulmuş bir finansal yapıdır (Author, Year). Bu yapı, gelişmiş bir emir eşleştirme motoru ve yüksek likiditeye sahip bir emir defterinden oluşur (Author, Year). Bir yatırımcının emrini en iyi fiyata gerçekleştirmek brokerin sorumluluğundadır (Author, Year). Broker, emri hisse senedi borsasına iletir ve buradaki eşleştirme motoru, alım emrini en iyi satım emriyle eşleştirir (Author, Year). Emirler eşleştikten sonra, hisse senedi borsası emir defterini işlem fiyatına göre günceller (Author, Year). FX borsası ise, dealer'ların döviz çiftleri ticareti yaptığı bir bankalararası borsadır (Author, Year). FX Aggregator veya FX Brokerage firmaları, perakende yatırımcılardan gelen emirleri toplar ve bu emirleri bankalararası piyasaya yönlendirir (Author, Year). Brokerin yönlendirme sistemi, öncelikle kendi dahili Alternatif Ticaret Sistemi'nde (ATS) eşleşen bir emir arar (Author, Year). Emir dahili ATS tarafından eşleştirilemezse, yönlendirme sistemi mevcut en iyi fiyatı bulmak için bağlı tüm borsaları ve ATS'leri tarar ve emri oraya yönlendirir (Author, Year).

Emir defteri dinamiklerini modellemek için çeşitli yaklaşımlar mevcuttur. Bir yaklaşım, limit emir defterini sürekli zamanlı bir Markov süreci olarak modellemeyi ve defterdeki her fiyat seviyesindeki limit emir sayısını izlemeyi içerir (Author, Year). Bu model, yüksek frekanslı verilere kolayca kalibre edilebilme, emir defterlerinin çeşitli ampirik özelliklerini yeniden üretebilme ve analitik olarak işlenebilir olma özelliklerini dengeler (Author, Year). Model, kuyruk teorisi literatüründen Laplace dönüşümü tekniklerini kullanarak çeşitli koşullu olasılıkları hesaplamak için yeterince basittir (Author, Year). Elektronik ticaret sistemlerinin yaygın olarak benimsenmesiyle birlikte, emir işleme süresindeki hızlı düşüş, yüksek hacimli, yüksek frekanslı ticarete yol açmıştır (Author, Year). Limit emir defteri dinamiklerini modelleme üzerine yapılan araştırmalar genellikle istatistiksel modelleme ve makine öğrenimi tabanlı yöntemler olmak üzere iki ana kategoriye ayrılabilir (Author, Year).

Bir diğer modelleme yaklaşımı, fiyat ve alış-satış farkını (bid-ask spread) tam emir defteri dinamikleriyle açıklamayı hedefler (Author, Year). Bu model, özellikle orta vadeli (birkaç dakika ila birkaç saat) zaman dilimlerinde, volatiliteye göre nispeten büyük spread boyutlarına sahip varlıklar için uygundur (Author, Year). Modelde, A(t) alış fiyatını, B(t) ise satış fiyatını temsil eder (Author, Year). Model, alış-satış süreçlerinin tam emir defterinden çok fazla bilgi içerdiğini ve tam emir defterinin doğrudan alış-satış süreçlerinin dinamiklerini etkilediğini belirtir (Author, Year).



## Technical Indicators for Cryptocurrency Trading

### Moving Averages in Cryptocurrency Trading
## Kripto Para Birimi Ticaretinde Hareketli Ortalamaların Rolü

Kripto para piyasaları, özellikle Bitcoin, son yıllarda yatırımcıların önemli ölçüde ilgisini çekmiştir. Bu bağlamda, teknik analiz araçları, yatırım kararlarını desteklemek amacıyla giderek daha fazla kullanılmaktadır. Hareketli ortalamalar (MA), teknik analizde yaygın olarak kullanılan temel bir araçtır ve kripto para birimi ticaretinde önemli bir rol oynamaktadır.

Bazı araştırmalar, Bitcoin getirilerinin, fiyatların hareketli ortalamalarına oranları ile günlük olarak tahmin edilebileceğini göstermektedir (Author, Year). Özellikle, fiyatın hareketli ortalamanın üzerinde olduğu durumlarda Bitcoin'de uzun pozisyon almayı ve aksi takdirde nakitte kalmayı öngören ticaret stratejilerinin, al-tut stratejisine kıyasla daha iyi performans gösterdiği, alfa değerlerini artırdığı ve Sharpe oranlarını 0,2 ila 0,6 oranında yükselttiği belirtilmektedir (Author, Year). Bu bulguların, örneklemin farklı bölümlerinde tutarlılık gösterdiği vurgulanmaktadır. Dahası, hareketli ortalama stratejilerinin, Bitcoin'in önde gelen rakipleri olan Ripple ve Ethereum için de al-tut stratejisinden daha iyi sonuçlar verdiği gözlemlenmiştir (Author, Year). Bu durum, yatırımcıların beklenen kolaylık getirisi büyüme oranı hakkındaki inançlarını yansıtan fiyat-MA oranları ile getirilerin tahmin edilebilir olduğunu desteklemektedir (Author, Year).

Teknik analiz, hareketli ortalama stratejisi gibi basit işlem kurallarını içermektedir (Author, Year). Hareketli ortalamalar üzerine kurulu kurallar daha önce İsviçre ve Latin Amerika/Asya pazarlarında uygulanmıştır (Author, Year). Trend bazlı stratejiler, cari fiyatların ve geçmiş fiyatların kesişimi sonucunda bir alım satım sinyali üretir (Author, Year). Örneğin, bir hisse senedinin 3 günlük en düşük ve hareketli ortalamanın altına düşmesi durumunda satmak, bu tür bir stratejinin tipik bir örneğidir (Author, Year).

Literatürde, derin öğrenme algoritmalarının Bitcoin'in yüksek frekanslı trend tahmininde kullanıldığı ve bazı araştırmaların umut verici sonuçlar verdiği belirtilmektedir (Author, Year). Örneğin, Alonso-Monsalve ve diğerleri (Author, Year), dakika bazındaki Bitcoin fiyatlarından hesaplanan 18 teknik göstergeyi kullanarak CNN, hibrit CNN-LSTM ağı, MLP ve RBF sinir ağları ile altı popüler kripto paranın fiyat değişikliklerini tahmin etmişlerdir. Çalışmanın sonucunda, hibrit CNN-LSTM ağının en iyi performansı gösterdiği ve Monero ve Dash'in fiyat değişikliklerini tahmin etmede %80 ve %74'e varan doğruluklara ulaştığı tespit edilmiştir (Author, Year).



### Relative Strength Index (RSI) in Cryptocurrency Trading
İşte geliştirilmiş akademik bölüm:

**Göreceli Güç Endeksi (RSI) ve Kripto Para Ticaretindeki Rolü**

Teknik analizde yaygın olarak kullanılan Göreceli Güç Endeksi (RSI), bir momentum osilatörü olarak fiyat hareketinin hızını ve değişimini değerlendirmek için tasarlanmıştır (Author, Year). Osilatörler, genel olarak momentumu ölçmek amacıyla kullanılır ve RSI gibi osilatörler, piyasanın aşırı alım veya aşırı satım koşullarında olup olmadığını belirlemeye yardımcı olabilir (Author, Year). Literatür, osilatörlerin trendin önemini vurguladığını ve özellikle trend piyasalarında kullanışlı olduğunu belirtmektedir (Author, Year). Bu nedenle, RSI, kripto para piyasalarındaki trendleri analiz etmek ve potansiyel alım-satım fırsatlarını belirlemek için değerli bir araç olarak kabul edilebilir.



### Moving Average Convergence Divergence (MACD) in Cryptocurrency Trading
İşte geliştirilmiş akademik bölüm:

**Kripto Para Birimi Ticaretinde Hareketli Ortalama Yakınsama Iraksama (MACD)**

Hareketli Ortalama Yakınsama Iraksama (MACD), finansal piyasa analizinde yaygın olarak kullanılan uyarlanabilir bir dijital bant geçiren filtredir (Author, Year). MACD filtresinin temel işlevi, düşük ve yüksek frekanslı bileşenleri ortadan kaldırmaktır (Author, Year). Bu özelliği, onu fNIRS sinyallerinin gerçek zamanlı bant geçiren filtrelemesi için uygun kılar (Author, Year). Aslında, düşük dereceli bir dijital filtre olarak önerilmiştir (Author, Year).

Filtrenin önemli bir özelliği, sinyalin ilk türevini tahmin edebilmesidir (Author, Year). Bu yetenek, ön öğrenme aşamasına ihtiyaç duymadan uyaran başlangıçlarının çevrimiçi tespiti için onu değerli bir araç haline getirir (Author, Year). Utsugi ve meslektaşları, fNIRS tabanlı Beyin-Bilgisayar Arayüzü (BCI) tasarımında gürültü azaltma amacıyla MACD'yi daha önce kullanmışlardır (Author, Year).

MACD filtresinin bant genişliği ve kesme frekansları, Nlong ve Nshort parametreleri arasındaki farka bağlıdır (Author, Year). Bu parametreler arasındaki ilişki, filtre özelliklerinin hassas bir şekilde ayarlanmasına olanak tanır (Author, Year). Bu ayarlanabilirlik, MACD'yi çeşitli kripto para birimi ticaret stratejileri için esnek bir araç haline getirebilir.



### Bollinger Bands in Cryptocurrency Trading
İşte geliştirilmiş akademik bölüm:

### Teknik Göstergeler: Kripto Para Ticaretinde Bollinger Bantlarının Değerlendirilmesi

Bu bölüm, kripto para ticaretinde teknik göstergelerin, özellikle de Bollinger Bantlarının kullanımını incelemektedir. Çalışma, kripto para birimleri, kripto para borsaları ve otomatik ticaret sistemleri hakkında genel bir çerçeve sunarak konuya zemin hazırlamaktadır (Yazar, Yıl). Kripto para piyasalarındaki arbitraj fırsatları ve fiyat oluşumu mekanizmaları, bu bağlamda özellikle vurgulanmaktadır (Yazar, Yıl).

Araştırmalar, kripto para piyasalarında önemli ve tekrarlayan arbitraj fırsatlarının varlığına işaret etmektedir (Yazar, Yıl). Fiyat farklılıklarının, ülke içi piyasalara kıyasla ülkeler arasında daha belirgin olduğu gözlemlenmektedir (Yazar, Yıl). Örneğin, 2017 Aralık ayından 2018 Şubat ayı başlarına kadar ABD ve Kore arasındaki günlük ortalama fiyat oranının %15'in üzerinde seyrettiği ve bazı günlerde %40'a ulaştığı belirtilmektedir (Yazar, Yıl). Bu fiyat sapmalarının, Bitcoin'in değer kazandığı dönemlerde daha da arttığı tespit edilmiştir (Yazar, Yıl). Bitcoin, genellikle ABD dışındaki ülkelerde primli işlem görürken, bu prim Bitcoin değer kazandığında arbitraj sapmalarını daha da artırmaktadır (Yazar, Yıl). Ülkeler arasındaki bu fiyat farklılıklarının, sermaye kontrolleri veya zayıf finansal kurumlar gibi faktörlerle açıklanabileceği öne sürülmektedir (Yazar, Yıl). Sermaye kontrollerinin, kripto para birimlerinden itibari paralara geçişi etkileyebileceği de belirtilmektedir (Yazar, Yıl).



### On-Balance Volume (OBV) in Cryptocurrency Trading
Here's the enhanced academic section, incorporating the provided content and citations, formatted for a research paper:

**On-Balance Volume (OBV) in Cryptocurrency Trading**

Technical analysis of investment cycles frequently relies on the interplay between price fluctuations and trading volume, with On-Balance Volume (OBV) functioning as a key technical indicator within this framework (Author, Year). OBV seeks to provide insight into the cumulative buying and selling pressure behind price movements. A related, more sophisticated technique, Block Volume Classification (BVC), offers an alternative approach to analyzing volume data (Author, Year). BVC aggregates trades based on either time or volume intervals and subsequently calculates the percentage of buy and sell orders, utilizing the price change between the close of the current bar and the close of the preceding bar (Author, Year).

The primary objective of BVC is to identify both aggressive and passive informed trading activities, with the potential to surpass the performance of traditional order imbalances (Author, Year). Order imbalances, in their conventional form, quantify the disparity between aggressive buying volume and aggressive selling volume within a defined time period (Author, Year). In contrast to transaction-by-transaction classification, the BVC algorithm employs a bar-based buy-sell probability (Author, Year). This involves aggregating transactions into bars determined by volume or time, and then employing a standardized price change from the beginning to the end of the interval to estimate the proportion of buy and sell order flow (Author, Year).

While research indicates a positive correlation between BVC-derived order imbalance and the high-low spread of price movement, some studies question its efficacy in accurately measuring informed trading (Author, Year). Specifically, these investigations suggest that BVC may not consistently outperform traditional order imbalances and, in some testing scenarios, may even significantly underperform them (Author, Year).



### Fibonacci Retracement in Cryptocurrency Trading
İşte geliştirilmiş akademik bölüm:

**Fibonacci Düzeltmesi: Bitcoin Ticaretinde Bir Vaka Çalışması**

Teknik analizde yaygın olarak kullanılan bir araç olan Fibonacci düzeltmesi, kripto para birimi ticaretinde potansiyel destek ve direnç seviyelerini belirlemek için uygulanmaktadır. Bu bağlamda, Pambudi (2023), Bitcoin alım satım kararlarını belirlemede Fibonacci, RSI ve MACD algoritmalarının kullanımını inceleyen bir çalışma yürütmüştür. Araştırma, Fibonacci algoritmasının Bitcoin alım satım kararlarını belirlemedeki hesaplama koşullarını ve bu algoritmaların Bitcoin alım satım işlemlerindeki karar verme doğruluğunu değerlendirmeyi amaçlamıştır (Pambudi, 2023).

Pambudi (2023) tarafından yürütülen bu çalışma, Zipmex uygulamasındaki Bitcoin fiyatları üzerinde 21 Nisan - 12 Haziran 2022 tarihleri arasındaki Fibonacci, RSI ve MACD kullanımını inceleyen bir vaka çalışması kullanmıştır. Bulgular, Fibonacci, RSI ve MACD algoritmalarının hesaplama koşullarının kapanış fiyatlarına yakın olduğunu ve Bitcoin için alım satım kararları vermede öneriler sağlayabileceğini göstermiştir (Pambudi, 2023). Dahası, Fibonacci, RSI ve MACD algoritmalarına dayalı Bitcoin alım satım kararlarının doğruluğunun, işlem kararları için öneriler sunmada oldukça doğru olduğu belirtilmiştir (Pambudi, 2023). Bu sonuçlar, Fibonacci düzeltmesinin diğer teknik göstergelerle birlikte kullanıldığında Bitcoin ticaretinde karar verme süreçlerini destekleyebileceğine işaret etmektedir.



### Ichimoku Cloud in Cryptocurrency Trading
## Teknik Göstergeler: Kripto Para Ticaretinde Ichimoku Bulutu

Kripto para piyasaları, yüksek volatilite ve 24/7 işlem imkanı sunmasıyla bilinir. Bu dinamik ortamda, yatırımcılar karar alma süreçlerini desteklemek ve potansiyel kar fırsatlarını belirlemek için çeşitli teknik analiz araçlarına başvurmaktadır. Bu araçlardan biri de Ichimoku Bulutu'dur. Ancak, bu çalışma kapsamında, kripto para ticaretinde Ichimoku Bulutu'nun kullanımına dair spesifik bir literatür taraması yapılmış olmasına rağmen, bu alt başlıkla doğrudan ilgili herhangi bir bilgiye rastlanmamıştır (Author, Year). Bu durum, kripto para piyasalarında Ichimoku Bulutu'nun kullanımının ya henüz yeterince araştırılmamış bir alan olduğunu ya da mevcut araştırmaların farklı anahtar kelimeler altında sınıflandırıldığını göstermektedir.

Bu nedenle, kripto para ticaretinde Ichimoku Bulutu'nun etkinliğini değerlendirmek için daha fazla araştırmaya ihtiyaç duyulmaktadır. Gelecekteki çalışmalar, farklı kripto para birimleri ve zaman dilimleri üzerinde Ichimoku Bulutu'nun performansını analiz ederek, bu göstergenin kripto para piyasalarındaki potansiyel faydalarını ve sınırlamalarını daha iyi anlamamıza yardımcı olabilir. Ayrıca, Ichimoku Bulutu'nun diğer teknik göstergelerle kombinasyonunun, kripto para ticaretinde daha doğru ve güvenilir sinyaller üretip üretmediği de araştırılması gereken önemli bir konudur (Author, Year).



## Performance Evaluation Metrics for Indicator Combinations

### Profitability Metrics for Cryptocurrency Trading Strategies
## Kripto Para Ticaret Stratejileri için Karlılık Metrikleri

Teknik ticaret stratejilerinin etkinliği, kripto para piyasalarında sıklıkla incelenen bir araştırma konusudur. Bu stratejiler, piyasa verilerini girdi olarak kullanarak belirli bir zaman dilimi için alım satım kararları üretmektedir (Author, Year). Mevcut literatür, basit teknik ticaret stratejilerinin davranışlarını ve istatistiksel özelliklerini analiz ederek karlılık ve ticaret doğruluğunu karşılaştırmaktadır (Author, Year). Bu bağlamda, filtre stratejileri, hareketli ortalama (MA) stratejileri ve aritmetik ve harmonik ortalama farkı stratejileri gibi çeşitli yaklaşımlar değerlendirilmektedir (Author, Year).

Hareketli ortalama oranlarının, günlük Bitcoin getirilerini tahmin etme potansiyeli olduğu belirtilmektedir. Bu oranlara dayalı ticaret stratejileri, al-tut stratejilerine kıyasla önemli alfa ve Sharpe oranı kazançları sağlayabilmektedir (Author, Year). Örneğin, fiyatın hareketli ortalamanın üzerinde olduğu durumlarda Bitcoin'de uzun pozisyon alıp, aksi takdirde nakitte uzun pozisyon alan stratejiler, al-tut kıyaslamasına göre daha iyi performans göstermekte, yüksek alfalar üretmekte ve Sharpe oranlarını 0,2 ila 0,6 oranında artırmaktadır (Author, Year). Hareketli ortalama stratejilerinin, Bitcoin'in rakipleri olan Ripple ve Ethereum için de al-tut stratejilerinden daha iyi sonuçlar verdiği gözlemlenmiştir (Author, Year).

Bununla birlikte, ticaret stratejilerini değerlendirirken çoklu testlerin dikkate alınması kritik öneme sahiptir. Birçok strateji ve kombinasyonunun denenmesi durumunda, Sharpe oranları gibi istatistikler abartılabilir (Author, Year). Ortalama karlılık, tutarlılık ve düşüşlerin büyüklüğü gibi faktörler tek başına bir stratejiyi değerlendirmek için yeterli değildir ve çoklu testler için düzeltmeler yapılması gerekmektedir (Author, Year). Sharpe oranı 0,92 olan bir ticaret stratejisi örneğinde, t-istatistiği 2,91 olarak hesaplanmıştır. Bu, gözlemlenen karlılığın sıfır karlılık hipotezinden yaklaşık üç standart sapma uzakta olduğunu göstermektedir. Ancak, çoklu testler dikkate alınmadığında istatistiksel anlamlılık yanıltıcı olabilir ve istatistiksel anlamlılık oluşturmak için eşikler ayarlanmalıdır (Author, Year).

Son olarak, kripto para birimlerinin yüksek varyanslarının sonraki haftalarda daha düşük getirilere yol açtığı belirtilmektedir (Author, Year). Pozitif sıçrama ve sıçramaya dayanıklı varyanslar da getirileri negatif etkilemektedir. Bu negatif fiyatlama etkisi, daha küçük, daha düşük fiyatlı, daha az likit, daha fazla perakende yatırımcı aktivitesine sahip ve daha olumlu duyguya sahip kripto para birimleri için daha belirgindir (Author, Year). Yüksek toplam ve pozitif sıçrama varyanslarına sahip kripto para birimleri, düşük varyanslı olanlara göre daha küçük boyutlara, daha düşük fiyatlara ve daha geniş alış-satış farklarına sahiptir. Ayrıca, yüksek varyanslı kripto para birimlerinde daha yüksek işlem hacimleri gözlemlenmektedir, bu da gelecekteki fiyatlar hakkında önemli bir anlaşmazlık olduğunu göstermektedir (Author, Year). Perakende yatırımcıların yüksek volatiliteye sahip menkul kıymetleri tercih etmesi ve risk almaya istekli olması, bu durumun önemli bir faktörü olarak değerlendirilmektedir (Author, Year).



### Risk-Adjusted Return Metrics for Cryptocurrency Trading Strategies
## Kripto Para Ticaret Stratejileri için Risk Düzeltilmiş Getiri Metrikleri

Kripto para piyasalarının kendine özgü yapısı, geleneksel finansal varlıklardan farklı bir performans değerlendirme metodolojisi gerektirmektedir. Kripto varlık getirileri, yüksek volatilite, kalın kuyruklar, aşırı basıklık ve çarpıklık gibi özellikler sergilemektedir (Author, Year). Bu durum, geleneksel risk tahsis yöntemlerinin basit bir şekilde uygulanmasının, kripto varlıklarını daha geniş yatırım stratejilerine entegre etmek için yeterli olmayabileceğini göstermektedir (Author, Year). Bu bağlamda, kripto para ticaret stratejilerinin performansını değerlendirmek amacıyla risk düzeltilmiş getiri metriklerinin kullanımı büyük önem arz etmektedir.

Sharpe oranı, getiriyi oynaklıkla (bir risk ölçüsü) normalleştirerek riski hesaba katan yaygın olarak kullanılan bir performans ölçüsüdür (Author, Year). Daha düşük oynaklığa sahip stratejiler, daha yüksek Sharpe oranlarına sahiptir ve sektörde üç yıllık bir geçmiş kabul edilebilir olarak değerlendirilirken, üç yılı aşkın bir sürede 2 veya daha yüksek bir Sharpe oranı oldukça iyi olarak kabul edilmektedir (Author, Year). Bununla birlikte, Sharpe oranının yukarı yönlü ve aşağı yönlü riski eşit olarak cezalandırması, kripto para piyasalarının asimetrik getiri dağılımları göz önüne alındığında bir sınırlama olarak değerlendirilebilir (Author, Year). Bu sorunu gidermek amacıyla, aşağı yönlü sapma oranı (Downside Deviation Ratio), yalnızca negatif getirileri dikkate alarak hesaplanan bir alternatif olarak sunulmaktadır (Author, Year).

Maksimum geri çekilme (MDD), birikimli getiri eğrisinin en büyük olası kaybını ölçer ve getirilerin permütasyonlarına duyarlıdır (Author, Year). Sterling oranı ise, getirinin MDD'ye bölünmesiyle elde edilen bir diğer yaygın risk düzeltilmiş getiri ölçüsüdür ve hedge fonları genellikle küçük MDD'lere sahip olmayı tercih etmektedirler (Author, Year).

Geleneksel CAPM benzeri kıyaslamaların hatalı sonuçlara yol açabileceği durumlarda, stokastik iskonto faktörü yaklaşımı kullanılarak momentum stratejilerinin karlılığı değerlendirilebilir (Author, Year). Nonparametrik risk ayarlamasının momentum stratejisi karlarının önemli bir bölümünü açıklayabileceği ve risk ölçülerinin piyasa risk primi arttıkça artması gerektiği belirtilmektedir (Author, Year).

Hisse senedi getirileri normal dağılmadığında, risk-ayarlı hisse senedi sıralama kriterleri, olağan kümülatif getiri kriterine göre daha karlı momentum stratejileri oluşturabilir (Author, Year). Bu alternatif risk-getiri oranı kriterleri, kuyruk dağılımının riskini yakalar ve portföy optimizasyon probleminde amaç fonksiyonu olarak kullanılabilir (Author, Year). Sharpe oranı gibi geleneksel risk ayarlı ölçüler uygulanabilir olsa da, Sharpe oranı paydanın düşük değerleri için kararsızdır ve temel veriler normallik varsayımından saptığında güvenilir değildir (Author, Year). Risk-getiri oranları, hisse senedi sıralama sürecini yönlendirmek ve kazanan ve kaybeden portföylerin risk-getiri profilini değerlendirmek ve optimize etmek için bireysel menkul kıymet düzeyinde uygulanabilir (Author, Year). Bu nedenle, optimal riskli kazanan ve kaybeden portföyler oluşturan optimize edilmiş ağırlıklı bir strateji geliştirilebilir (Author, Year).



### Sharpe Ratio for Cryptocurrency Trading Strategies
## Kripto Para Ticaret Stratejileri için Sharpe Oranı

Sharpe oranı (SR), bir yatırımın risk düzeltilmiş getirisini değerlendirmek için yaygın olarak kullanılan bir performans ölçütüdür ve fazla beklenen getirinin getiri standart sapmasına oranı olarak tanımlanır: (µ - Rf) / σ (Author, Year). Bununla birlikte, beklenen getiriler ve oynaklıklar genellikle doğrudan gözlemlenemeyen nicelikler olduğundan, geçmiş veriler kullanılarak tahmin edilmeleri gerekmektedir ve bu durum kaçınılmaz olarak tahmin hatalarına yol açmaktadır (Author, Year). Sonuç olarak, Sharpe oranı da hatayla tahmin edilmektedir (Author, Year). Sharpe oranı tahmin edicilerinin doğruluğu, getirilerin istatistiksel özelliklerine bağlıdır ve bu özellikler portföyler, stratejiler arasında ve zaman içinde önemli ölçüde değişiklik gösterebilir (Author, Year). Dahası, aylık verilerden yıllık Sharpe oranını hesaplarken, getirilerin serisel korelasyonu önemli bir etkiye sahip olabilir ve aylık tahminleri çarparak Sharpe oranlarını yıllıklandırma uygulaması yalnızca belirli koşullar altında geçerlidir (Author, Year).

Hisse senedi piyasalarında, Sharpe oranlarındaki öngörülebilir zamanla değişim belgelenmiştir (Author, Year). Araştırmalar, önceden belirlenmiş finansal değişkenlerin hisse senedi getirilerinin koşullu ortalamasını ve oynaklığını tahmin etmek için kullanıldığını ve bu momentlerin koşullu Sharpe oranını tahmin etmek için birleştirildiğini göstermiştir (Author, Year). Elde edilen tahmini koşullu Sharpe oranları, iş döngüsünün evreleriyle örtüşen önemli zamanla değişim sergilemektedir; döngünün zirvesinde Sharpe oranları genellikle düşükken, çukurda yüksektir (Author, Year).

Kripto para piyasalarında da Sharpe oranı, çeşitli ticaret stratejilerinin performansını değerlendirmek için kullanılmaktadır. Örneğin, fiyatların hareketli ortalamalarına (MA) oranları, günlük Bitcoin getirilerini örnek içi ve örnek dışı olarak tahmin etmede etkili bulunmuştur (Author, Year). Bu oranlara dayalı ticaret stratejileri, al-ve-tut pozisyonuna kıyasla ekonomik olarak anlamlı bir alfa ve Sharpe oranı kazancı üretmektedir (Author, Year). Fiyat MA'nın üzerindeyken Bitcoin'e uzun pozisyon alan ve aksi takdirde nakitte uzun pozisyon alan bir ticaret stratejisinin, al-ve-tut kıyaslamasından önemli ölçüde daha iyi performans gösterdiği ve Sharpe oranlarını 0,2 ila 0,6 oranında artırdığı gözlemlenmiştir (Author, Year). Benzer şekilde, derin öğrenme teknikleri (CNN ve LSTM ağları) kullanılarak dakika seviyesindeki teknik göstergelerle Bitcoin fiyatlarının yüksek frekanslı trend tahminleri yapılmış ve geliştirilen modelin, net varlık değeri ve Sharpe oranı açısından Bitcoin'leri pasif olarak tutma stratejisinden daha iyi performans gösteren ticaret stratejileri üretebildiği gösterilmiştir (Author, Year). Alonso-Monsalve ve diğerleri (Author, Year), CNN, hibrit CNN-LSTM ağı, MLP ve RBF sinir ağını kullanarak altı popüler kripto para biriminin (Bitcoin, Dash, Ether, Litecoin, Monero ve Ripple) fiyat değişikliklerini tahmin etmiş ve hibrit CNN-LSTM ağının en iyi performansı gösterdiğini tespit etmiştir.



### Sortino Ratio for Cryptocurrency Trading Strategies
## Kripto Para Ticaret Stratejileri için Performans Değerlendirme Metrikleri: Sortino Oranı

Kripto para piyasalarının yüksek getiri potansiyeli, eş zamanlı olarak yüksek oynaklık seviyeleriyle dengelenmektedir. Bu durum, geleneksel varlık sınıflarıyla karşılaştırıldığında, kripto para ticaret stratejilerinin performansını değerlendirmek için uygun metriklerin seçimini kritik bir öneme sahip kılmaktadır. Literatürde, Sharpe oranı gibi yaygın olarak kullanılan performans değerlendirme ölçütlerine alternatif yaklaşımlar önerilmiştir (Author, Year). Bu alternatifler, genellikle paydada aşağı yönlü bir dağılım ölçüsü kullanarak riski daha hassas bir şekilde yakalamayı hedefleyen ödül-değişkenlik oranlarıdır (Author, Year).

Bu bağlamda, Sortino oranı, Sharpe oranına kayda değer bir alternatif olarak öne çıkmaktadır. Sortino oranı, değişkenlik ölçüsü olarak aşağı yönlü yarı standart sapmayı kullanır (Author, Year). Sharpe oranı, portföy getirisinin hem yukarı hem de aşağı yönlü potansiyelini cezalandırdığı için, özellikle asimetrik getiri dağılımlarına sahip varlıklar için her zaman uygun bir performans ölçüsü olmayabilir (Author, Year). Sortino-Satchell oranı ise, ortalama aktif getiriyi portföy getiri dağılımının daha düşük bir kısmi momentiyle bölerek benzer bir yaklaşım sergilemektedir (Author, Year).

Ödül-risk oranları (RRR'ler) genel olarak finansal karar verme süreçlerinde yaygın olarak kullanılan performans ölçütleridir (Author, Year). Bununla birlikte, mevcut RRR'lerin yapısal eksiklikleri bulunmaktadır. Örneğin, Sharpe oranının monoton olmaması, bir yatırımın diğerine tercih edilmesine yol açabileceği durumlar yaratabilir; bu durum, her yatırımın olası her senaryoda daha yüksek getiri sağlamasına rağmen gerçekleşebilir (Author, Year). Bu nedenle, iyi yapısal özelliklere sahip RRR'ler için monotonluk ve yarı-içbükeylik önemli kriterlerdir (Author, Year). Monotonluk, daha fazlasının daha azından daha iyi olduğu prensibini ifade ederken, yarı-içbükeylik ortalamalara aşırılıklardan daha fazla değer veren ve böylece çeşitlendirmeyi teşvik eden tercihleri yansıtır (Author, Year). Bazı RRR'ler, Sharpe oranı gibi, ölçekten bağımsızdır ve yalnızca bir getiri dağılımına bağlıdır (Author, Year).

Hareketli ortalamalara (MA) dayalı ticaret stratejileri bağlamında, fiyatların MA'lara oranlarının Bitcoin getirilerini tahmin edebildiği ve al-tut stratejisine kıyasla önemli alfa ve Sharpe oranı kazançları sağlayabildiği gösterilmiştir (Author, Year). Fiyatın MA'nın üzerinde olduğu durumlarda Bitcoin'de uzun pozisyon alan bir ticaret stratejisi, al-tut kıyaslamasından daha iyi performans göstermekte ve Sharpe oranlarını artırmaktadır (Author, Year). Bu tür stratejiler, Ripple ve Ethereum gibi diğer kripto para birimlerinde de al-tut stratejisinden daha iyi performans sergilemiştir (Author, Year).

Sonuç olarak, kripto para ticaret stratejilerinin performansını değerlendirirken, risk ölçüsünün seçimi ve kullanılan performans metriklerinin yapısal özellikleri büyük önem taşımaktadır. Sortino oranı gibi alternatif metrikler, özellikle asimetrik getiri dağılımlarına sahip kripto para piyasalarında daha uygun ve kapsamlı bir değerlendirme sağlayabilir.



### Maximum Drawdown Analysis for Cryptocurrency Trading Strategies
## Kripto Para Ticaret Stratejileri için Maksimum Geri Çekilme Analizi

Kripto para ticaret stratejilerinin performans değerlendirmesinde, maksimum geri çekilme (MDD) analizi önemli bir metodoloji olarak öne çıkmaktadır. MDD, bir yatırımın yaşam döngüsü boyunca gözlemlenen en büyük zirveden dibe düşüşü temsil eder (Anonim, Tarih Yok). Yatırımcılar, yöneticileri ve stratejileri değerlendirirken bu metriği yakından incelemektedir (Anonim, Tarih Yok). MDD, getirilerin gerçekleşme sırasına duyarlıdır, ancak pozitif getirileri cezalandırmaz (Anonim, Tarih Yok). MDD'nin hesaplanması için basit bir algoritma kübik karmaşıklığa sahip olsa da, doğrusal zamanda da hesaplanabilir (Anonim, Tarih Yok).

Geri çekilme kavramı, portföy değerinin geçmişte ulaşılan en yüksek değere kıyasla yaşadığı düşüşü ifade eder (Anonim, Tarih Yok). Bu düşüş, mutlak değerler veya göreceli (yüzde) terimlerle ifade edilebilir (Anonim, Tarih Yok). Bu bağlamda, Koşullu Geri Çekilme Riski (CDaR), portföy getirisi örnek yollarında tanımlanan ve portföy geri çekilme eğrisine bağlı olan yeni bir risk fonksiyonları ailesini temsil etmektedir (Anonim, Tarih Yok). CDaR, tolerans parametresi α'nın belirli bir değeri için, en kötü %100(1-α) geri çekilmelerin ortalaması olarak tanımlanır (Anonim, Tarih Yok). Örneğin, %0,95-CDaR (veya %95-CDaR), dikkate alınan zaman aralığında en kötü %5 geri çekilmenin ortalamasını ifade eder (Anonim, Tarih Yok). CDaR risk fonksiyonu, ortalama geri çekilmeyi ve maksimum geri çekilmeyi sınırlandırıcı durumlar olarak içerir ve geri çekilmelerin hem büyüklüğünü hem de süresini dikkate alır (Anonim, Tarih Yok).

MDD'nin analitik incelenmesi genellikle sıfır sürüklenmeli bir Brown hareketi varsayımı altında gerçekleştirilmiştir (Anonim, Tarih Yok). Bu çerçevede, X(t) aritmetik bir Brown hareketini temsil eder: dX(t) = µdt + σdW(t), burada µ ortalama getiriyi, σ standart sapmayı ve dW(t) Wiener artışını ifade etmektedir (Anonim, Tarih Yok). Geri çekilme (DD), 0'da yansıyan bir Brown hareketidir (Anonim, Tarih Yok). E[MDD(µ, σ, T)] için bir teorem sunulmuş ve uzun vadede E[MDD]'nin asimptotik davranışı incelenmiştir (Anonim, Tarih Yok).

Risk düzeltilmiş getiri ölçütleri arasında, getirinin MDD'ye bölünmesiyle elde edilen Sterling oranı yaygın olarak kullanılmaktadır (Anonim, Tarih Yok). Hedge fonları genellikle küçük MDD'lere sahip olmayı tercih ederler, zira büyük düşüşler fon itfalarına yol açabilmektedir (Anonim, Tarih Yok). Ayrıca, Calmar oranını en üst düzeye çıkarmak için portföy optimizasyonu da incelenmektedir (Anonim, Tarih Yok). MDD ve Sterling tipi oranlar için ölçekleme yasaları mevcuttur (Anonim, Tarih Yok). Normalleştirilmiş Calmar oranı ve göreli güç kavramları tanıtılmıştır ve göreli güç, toplam bir düzen tanımlamaktadır (Anonim, Tarih Yok).

Kripto para piyasasının yüksek volatiliteye sahip olması nedeniyle, risk yönetimi stratejileri büyük önem arz etmektedir (Anonim, Tarih Yok). Volatilite hedefleme yöntemleri riski kontrol etmede etkili bulunmuştur ve trend takip stratejileri iyi performans sergilemiştir (Anonim, Tarih Yok). Geri çekilme bazlı kurallar, yöneticilerin performanslarını kaybetme olasılığı olduğunda daha uygundur ve geri çekilme limitleri, varlıkların yönetildiği süreye göre dinamik olarak ayarlanmalıdır (Anonim, Tarih Yok). Gerçekleşen geri çekilmeleri yorumlarken, Tip I hatalarının (iyi yöneticileri işten çıkarma) ve Tip II hatalarının (kötü yöneticileri tutma) göreli maliyetleri dikkate alınmalıdır (Anonim, Tarih Yok). "Geri çekilme Yunanlıları" (drawdown Greeks) olarak adlandırılan hassasiyetler, Sharpe oranı, değerlendirme zaman aralığı ve getirilerin otokorelasyonu gibi temel faktörlerin belirli bir geri çekilme seviyesine ulaşma olasılığını nasıl etkilediğini incelemektedir (Anonim, Tarih Yok).



### Win Rate Analysis for Cryptocurrency Trading Strategies
### Kripto Para Ticaret Stratejileri için Kazanma Oranı Analizi

Kripto para piyasalarının karakteristik özelliği olan yüksek volatilite, etkili ticaret stratejilerinin geliştirilmesini zorunlu kılmaktadır. Bu bağlamda, bazı araştırmalar, Bitcoin getirilerinin fiyatların hareketli ortalamalarına (MA) oranları ile günlük olarak tahmin edilebileceğini öne sürmektedir (Author, Year). Bu oranlara dayalı ticaret stratejileri, pasif al-tut pozisyonuna kıyasla ekonomik olarak anlamlı alfa ve Sharpe oranı kazanımları sağlamaktadır (Author, Year). Örneğin, fiyatın hareketli ortalamanın üzerinde olduğu durumlarda Bitcoin'de uzun pozisyon alan ve aksi takdirde nakitte kalan bir ticaret stratejisinin, al-tut kıyaslamasından belirgin şekilde daha iyi performans gösterdiği, önemli alfalar ürettiği ve Sharpe oranlarını 0,2 ila 0,6 oranında artırdığı tespit edilmiştir (Author, Year). Benzer şekilde, 1 ila 20 haftalık hareketli ortalamalar (MA'lar) kullanılarak Bitcoin getirilerinin tahmin edilebilirliği gösterilmiştir (Author, Year). Fiyat hareketli ortalamanın üzerindeyse Bitcoin'de uzun pozisyon almak ve aksi takdirde nakitte kalmak, al-tut stratejisine kıyasla üstün sonuçlar vermektedir (Author, Year). Hareketli ortalama sinyallerinin Bitcoin'de uzun pozisyonu işaret ettiği günlerdeki ortalama getirilerin, nakit pozisyonunu işaret ettiği günlere kıyasla önemli ölçüde daha yüksek olduğu belirtilmektedir (Author, Year).

Bu stratejilerin etkinliği, Bitcoin'in önde gelen rakipleri olan Ripple ve Ethereum gibi diğer kripto para birimlerinde de değerlendirilmiştir. Elde edilen bulgular, hareketli ortalama stratejilerinin bu kripto para birimlerinde de al-tut kıyaslamasına göre daha iyi bir performans sergilediğini ortaya koymaktadır (Author, Year).

Alternatif yaklaşımlar da literatürde incelenmiştir. Örneğin, Twitter verilerinin kripto para birimi ticaret stratejileri geliştirmek amacıyla kullanılıp kullanılamayacağı araştırılmıştır (Author, Year). Bu amaçla, fiyatları Twitter verileriyle ilişkilendirerek ticaret için en uygun zamanlamayı belirleme metodolojisi uygulanmıştır. Belirli bir dijital para biriminin fiyatının belirli bir zaman aralığında artıp artmayacağını veya azalmayacağını tahmin etmek amacıyla destek vektör makineleri, lojistik regresyon ve Naive Bayes gibi denetimli makine öğrenimi algoritmaları kullanılmıştır (Author, Year). Bitcoin ile ilgili toplanan 1 milyondan fazla tweet kullanılarak, her algoritmanın Bitcoin'in fiyatının belirli bir zaman diliminde artıp artmayacağını öngörmesi amaçlanmıştır (Author, Year).



## Backtesting Methodologies for Cryptocurrency Trading Strategies

### Backtesting Frameworks for Cryptocurrency Trading
## Kripto Para Birimi Ticaretinde Geriye Dönük Test Çerçeveleri

Kripto para birimi ticaret stratejilerinin geliştirilmesi ve değerlendirilmesinde geriye dönük testler kritik bir öneme sahiptir. Bu bağlamda, çeşitli çerçeveler ve metodolojiler, stratejilerin geçmiş verilere dayalı performansını analiz etmek amacıyla geliştirilmiştir. Bu bölüm, kripto para birimi ticaretinde yaygın olarak kullanılan bazı önemli geriye dönük test çerçevelerini ve yaklaşımlarını inceleyecektir.

**Özel Geriye Dönük Test Platformları:**

Bazı araştırmalar, çoklu borsa API'lerine bağlanarak piyasa verilerini toplamak ve farklı piyasa çiftlerinde otomatik emirler vermek üzere özel kripto para birimi ticaret platformlarının tasarımına ve uygulanmasına odaklanmaktadır (Yazar, Yıl). Bu platformlar, genellikle yeni kripto para birimi borsa API'lerinin entegrasyonuna izin verecek şekilde tasarlanmıştır ve gerçek zamanlı piyasa verilerine dayalı olarak çeşitli ticaret stratejilerinin yapılandırılmasına olanak tanır (Yazar, Yıl). Bu tür platformlar, farklı kripto para borsalarından gerçek zamanlı olarak en önemli finansal verileri toplayabilen ve bu bilgileri yerel olarak saklayabilen bir sistemin tasarımını ve uygulanmasını içerir (Yazar, Yıl). Bu, özellikle büyük boyutlu verileri işlemek için tasarlanmış bir Zaman Serisi Veritabanı aracılığıyla uygulanır ve bu veriler araştırma, temel analiz ve strateji geriye dönük testi için kullanılır (Yazar, Yıl). Ayrıca, bu platformlar, yukarıda bahsedilen veritabanını kullanarak bir ticaret stratejisine dayalı olarak bir kripto para borsasına emir gönderebilen otomatik bir işlem sisteminin tasarımını ve uygulanmasını da içerir (Yazar, Yıl). Bu sistemler, yüksek düzeyde otomasyon sağlamak için bir kripto para borsası API'sine (Uygulama Programlama Arayüzü) bağlanır ve kullanıcının platformla minimum düzeyde etkileşim kurmasına olanak tanır (Yazar, Yıl). Platformlar, yeni borsa API'lerinin uygulanmasını sağlayacak şekilde tasarlanır ve her durum için en uygun borsaya karar vermek için borsa özellikleri arasında bir analiz yapılır (Yazar, Yıl). Dikkate alınacak özelliklerden bazıları şunlardır: likidite, işlem maliyetleri, güvenilirlik, bağlantı ve sunulan dijital para sayısı (Yazar, Yıl).

**FinRL-Meta Kütüphanesi:**

Finansal takviyeli öğrenme için açık kaynaklı bir çerçeve olan FinRL-Meta kütüphanesi, finansal verilerin düşük sinyal-gürültü oranı, geçmiş verilerin hayatta kalma yanlılığı ve geriye dönük test aşamasındaki model aşırı uyumu gibi zorlukları ele almayı amaçlar (Yazar, Yıl). FinRL-Meta, gerçek dünya piyasalarından dinamik veri kümeleri toplayan ve bunları spor salonu tarzı piyasa ortamlarına işleyen otomatik bir boru hattı aracılığıyla yüzlerce piyasa ortamı sağlar (Yazar, Yıl). Ayrıca, kullanıcıların yeni ticaret stratejileri tasarlamasına yardımcı olmak için popüler makaleleri yeniden üretir ve kullanıcıların sonuçlarını görselleştirmesi ve topluluk çapında yarışmalar yoluyla göreceli performansı değerlendirmesi için bulut platformlarında kıyaslamalar tutar (Yazar, Yıl). FinRL, hisse senedi ticareti, portföy tahsisi ve kripto ticareti gibi üç piyasa ortamını içerir (Yazar, Yıl).

**Risk Yönetimi ve Geriye Dönük Test:**

Risk yönetimi bağlamında, Value-at-Risk (VaR) ve Expected Shortfall (ES) tahminlerinin doğruluğunu değerlendirmek üzere iki aşamalı bir geriye dönük test prosedürü önerilmektedir (Yazar, Yıl). Bu prosedür, çeşitli koşullu volatilite modelleri (ARCH modelleri) ve dağılım varsayımları (normal, GED, Student-t, skewed Student-t) kullanılarak farklı finansal piyasalar ve ticaret pozisyonları için en iyi modelin bulunmasını amaçlar (Yazar, Yıl). Geriye dönük test sürecinde, modellerin VaR'ı doğru tahmin etme ve VaR'ın ötesindeki kayıpları öngörme yetenekleri değerlendirilmektedir (Yazar, Yıl). Çalışmalar, farklı piyasalar (hisse senedi borsaları, emtialar, döviz kurları) ve ticaret pozisyonları için en iyi risk yönetimi tekniklerini karşılaştırmaktadır (Yazar, Yıl). Modellerin istatistiksel doğruluğunu test etmek için, ihlal sayısının beklenen sayıya eşit olup olmadığı ve ihlallerin bağımsız dağılıp dağılmadığı incelenmektedir (Yazar, Yıl).

**Çoklu Testler ve Veri Madenciliği:**

Yeni bir ticaret stratejisi sunulduğunda, sonuçlar genellikle gerçek olamayacak kadar iyi görünür ve bu durum genellikle veri madenciliğinden kaynaklanır (Yazar, Yıl). Harvey ve Liu (Yazar, Yıl), çoklu testleri sistematik olarak hesaba katan ve herhangi bir Sharpe oranı için uygun "haircut"ı (düzeltmeyi) sağlayan istatistiksel bir çerçeve önermektedir. Bu yöntem, önerilen stratejiler için minimum karlılık eşikleri belirlemek için idealdir ve yatırımcıların önerilen bir stratejinin uygulanabilirliği konusunda gerçek zamanlı kararlar almasına olanak tanır (Yazar, Yıl). Harvey ve Liu'nun yöntemi, stratejilerin korelasyonunu açıkça hesaba katar (Yazar, Yıl). Gerçek "out-of-sample" testleri (geçmiş verilerin bir bölümünü ayırmak yerine), bir stratejinin uygulanabilirliğini değerlendirmek için daha temiz bir yoldur (Yazar, Yıl).

**Makine Öğrenimi ve Aşırı Uyum:**

Makine öğrenimi, yatırım yönetiminde umut vaat eden güçlü araçlar sunsa da, bu tekniklerin yanlış uygulanması hayal kırıklığına yol açabilir (Yazar, Yıl). Yatırım stratejilerinin geriye dönük testlerde aşırı uyumundan kaçınmak önemlidir (Yazar, Yıl). Araştırma protokolleri, yanlış keşiflere yol açabilecek bariz hataları en aza indirmek için tasarlanmıştır ve hem geleneksel istatistiksel yöntemlere hem de modern makine öğrenimi yöntemlerine uygulanır (Yazar, Yıl).

Sonuç olarak, kripto para birimi ticaret stratejilerinin geriye dönük testleri, özel platformlar, açık kaynaklı kütüphaneler ve risk yönetimi teknikleri de dahil olmak üzere çeşitli çerçeveler ve metodolojiler kullanılarak gerçekleştirilmektedir. Bu araçlar, stratejilerin performansını değerlendirmek ve potansiyel riskleri belirlemek için kullanılmaktadır. Ancak, veri madenciliği ve aşırı uyum gibi zorlukların farkında olmak ve uygun istatistiksel yöntemlerle bu sorunları ele almak, güvenilir ve sağlam sonuçlar elde etmek için kritik öneme sahiptir.



### Walk-Forward Optimization in Cryptocurrency Backtesting
## Kripto Para Birimi Geriye Dönük Testinde İleriye Dönük Optimizasyon: Literatürdeki Mevcut Durum

Kripto para birimi ticaret stratejilerinin performans değerlendirmesi için geriye dönük test metodolojileri kritik bir rol oynamaktadır. Bununla birlikte, mevcut literatürde ileriye dönük optimizasyon (walk-forward optimization) gibi spesifik geriye dönük test tekniklerine odaklanan çalışmaların sayısı sınırlıdır. Çeşitli araştırmalar portföy optimizasyonu, risk yönetimi ve Black-Litterman modeli gibi farklı konuları ele almakta, ancak ileriye dönük optimizasyon hakkında doğrudan ve kapsamlı bilgi sunmamaktadır (Author, Year). Bu durum, kripto para birimi ticaret stratejileri bağlamında ileriye dönük optimizasyonun etkinliğinin ve uygulanabilirliğinin daha derinlemesine incelenmesi ihtiyacını ortaya koymaktadır.

Geriye dönük test, doğru bir şekilde uygulandığında değerli bir doğrulama aracı olarak kabul edilmekle birlikte (Author, Year), aşırı uyum (overfitting) ve seçilim yanlılığı gibi potansiyel riskler barındırmaktadır. Aşırı uyum, modelin geçmiş verilere çok iyi uyum sağlaması ancak gelecekteki verilerde zayıf performans göstermesi durumudur. Çok sayıda geriye dönük testin gerçekleştirilmesi ve en iyi performansı gösteren testin tek bir deneme olarak sunulması, yanıltıcı sonuçlara yol açabilir ve finans alanındaki birçok yanlış keşfin temel nedeni olabilir (Author, Year). Ayrıca, ileriye dönük test ile yüksek Sharpe oranları elde etmenin nispeten kolay olduğu, ancak akademik çalışmaların bu süreçte yapılan deneme sayısını genellikle belirtmediği vurgulanmaktadır (Author, Year). Bu durum, sonuçların yorumlanmasında dikkatli olunması gerektiğini göstermektedir.

Bollerslev ve diğerleri (2016), tahmin değerlendirmesi için hareketli pencereler (rolling windows) yaklaşımını kullanmışlardır. Bu yöntemde, bir model belirli bir zaman aralığında (N uzunluğunda bir pencere) tahmin edilmekte ve ardından pencere bir adım ileri kaydırılarak tahmin işlemi tekrarlanmaktadır. Her adımda, modelin parametreleri yeniden tahmin edilmekte ve bir sonraki değer için bir tahmin oluşturulmaktadır. Tahmin hatası hesaplanmakta ve ortalama karesel tahmin hatası (MSE), modelin tahmin doğruluğunu ölçmek için kullanılmaktadır. Farklı modelleri karşılaştırmak için, her model için MSE hesaplanmakta ve daha düşük MSE'ye sahip model, örnek dışı tahminlerde daha iyi performans göstermektedir. Karşılaştırmaların adil olması için, her modelin aynı zaman dilimlerinde tahmin edilmesi gerekmektedir (Bollerslev et al., 2016). Bu yöntem, ileriye dönük optimizasyonun temel prensiplerini yansıtmakla birlikte, kripto para birimi ticaret stratejileri bağlamında doğrudan uygulanabilirliği ve etkinliği daha fazla araştırma gerektirmektedir.

Sonuç olarak, kripto para birimi ticaret stratejileri için ileriye dönük optimizasyonun kullanımı ve etkinliği hakkında daha fazla araştırmaya ihtiyaç duyulmaktadır. Mevcut literatür, geriye dönük testin potansiyel tuzaklarına ve sağlam teoriler geliştirmenin önemine dikkat çekmektedir (Author, Year). Bu nedenle, bu çalışma, ileriye dönük optimizasyonun kripto para birimi ticaret stratejileri üzerindeki etkisini daha derinlemesine incelemeyi amaçlamaktadır. Bu inceleme, kripto para birimi piyasalarında daha güvenilir ve sağlam ticaret stratejileri geliştirmeye katkıda bulunmayı hedeflemektedir.



### Overfitting Prevention in Cryptocurrency Backtesting
## Kripto Para Birimi Geriye Dönük Testlerinde Aşırı Uyumun Önlenmesi

Aşırı uyum (overfitting), bir modelin eğitim verilerine aşırı derecede iyi uyum sağlaması, ancak bağımsız test verilerinde daha düşük performans göstermesi durumunu ifade eder (Author, Year). Bu durum, modelin eğitim verilerindeki gürültüyü veya rastlantısal varyasyonları öğrenmesi ve dolayısıyla genelleme yeteneğinin azalmasıyla karakterize edilir (Author, Year). Kripto para birimi ticaret stratejilerinin geriye dönük testlerinde, aşırı uyumu önlemek amacıyla çeşitli metodolojiler geliştirilmiştir. Bu bölüm, bu metodolojileri ve ilgili kısıtlamaları incelemektedir.

### Aşırı Uyumun Önlenmesine Yönelik Yaklaşımlar

Aşırı öğrenmeyi engellemek için çeşitli yaklaşımlar mevcuttur (Author, Year). Bu yaklaşımlar genel olarak ceza yöntemleri, doğrulama ve çapraz doğrulama yöntemleri ve topluluk yöntemleri olarak sınıflandırılabilir.

**Ceza Yöntemleri:** Bu yöntemler, modelin karmaşıklığına bir ceza uygulayarak aşırı uyumu azaltmayı hedefler. Temel prensip, eğitim hatasını (εtrain) ve bir ceza terimini birleştirerek test hatasını (εtest) tahmin etmektir (Author, Year). Maksimum A Posteriori (MAP) gibi yöntemler, daha karmaşık hipotezlere daha düşük önsel olasılıklar atayarak cezalandırma mekanizması uygular (Author, Year). Bu yaklaşımda, amaç fonksiyonu (J) genellikle şu şekilde tanımlanır: J(w) = εtrain(w) + ceza(w) (Author, Year).

**Doğrulama ve Çapraz Doğrulama Yöntemleri:** Bu yöntemler, veri setini eğitim ve doğrulama kümelerine ayırarak aşırı uyumun ne zaman ortaya çıktığını deneysel olarak belirlemeyi amaçlar (Author, Year). K-katlı çapraz doğrulama, verileri k alt kümeye böler ve her bir alt kümeyi sırasıyla doğrulama kümesi olarak kullanarak modeli k kez eğitir (Author, Year). Holdout yöntemi, eğitim kümesinin bir alt kümesini (Seval) kullanarak hipotez uzayını ve karmaşıklığını belirlemeyi amaçlar (Author, Year). Çapraz doğrulama, holdout yöntemini birden çok kez tekrarlar ve sonuçları ortalamasını alır (Author, Year). Test seti yöntemi, verilerin bir kısmını test seti olarak ayırarak modelin gelecekteki performansı hakkında bir fikir edinmeyi amaçlar (Author, Year). Ancak, bu yöntem veri kaybına neden olabilir ve özellikle küçük veri setlerinde güvenilir sonuçlar vermeyebilir (Author, Year). Leave-one-out çapraz doğrulama (LOOCV) yöntemi, her bir veri noktasını ayrı ayrı test seti olarak kullanarak daha az veri kaybı sağlar, ancak hesaplama maliyeti yüksektir (Author, Year). k-fold çapraz doğrulama, veri setini k parçaya ayırarak her bir parçayı test seti olarak kullanır ve daha dengeli bir yaklaşım sunar (Author, Year).

**Topluluk Yöntemleri:** Bu yöntemler, birden fazla modelin tahminlerini birleştirerek daha iyi genelleme performansı elde etmeyi amaçlar (Author, Year). Tam Bayes yöntemleri, birçok hipotezi oylar. Torbalama (Bagging) ve Rastgele Ormanlar (Random Forests) diğer yaygın topluluk yöntemleridir (Author, Year). Torbalama, aşırı uyumun yüksek varyanstan kaynaklandığı durumlarda faydalı olabilir (Author, Year). Ensemble yöntemleri, birden fazla hipotezin birleşimini kullanır (Author, Year).

### Kısıtlamalar ve Dikkat Edilmesi Gerekenler

Makine öğrenimi algoritmaları, büyük veri miktarlarında aşırı uyumu önlemek için tasarlanmış olsa da, yatırım finansmanı alanında veri genellikle sınırlıdır ve çapraz doğrulama, boyutluluk lanetini (curse of dimensionality) tam olarak hafifletmeyebilir (Author, Year). Örneğin, k-katlı çapraz doğrulama ile 10 farklı hiperparametre ayarlamak, 50 yıllık verilerle getirileri tahmin etmeye çalışıyorsanız uygun bir yaklaşım olmayabilir (Author, Year). Hisse senedi verileri sınırlıdır ve çoğu makine öğrenimi uygulaması için yetersiz kalabilir (Author, Year). Yanlış bir stratejinin çapraz doğrulanmış örnekte başarılı olması mümkündür; bu durumda, çapraz doğrulama rastgele olmaktan çıkar ve tek bir tarihsel yol bulunabilir (Author, Year). Sınırlı veri nedeniyle güçlü aşırı uyum belirtileri gözlemlenmektedir (Author, Year). Bu nedenle, veri kümesini genişletmenin ve aşırı uyumu önlemenin yollarını araştırmak önemlidir (Author, Year).



### Data Snooping Bias in Cryptocurrency Backtesting
## Data Snooping Bias in Cryptocurrency Backtesting

Data snooping bias, also known as data mining, represents a significant threat to the validity of backtesting results. This bias arises when a single dataset is repeatedly employed for inference or model selection (White, 2000). The iterative use of data elevates the risk that seemingly robust results are, in fact, attributable to chance rather than the genuine efficacy of the employed methodology (White, 2000). While the perils of data snooping are widely acknowledged within the empirical research community, its prevalence remains a persistent concern (White, 2000). A primary impediment to mitigating this bias is the relative scarcity of readily applicable methods for assessing its potential impact within a specific context (White, 2000). In the realm of financial time series analysis, this challenge is particularly acute due to the limited availability of historical data pertaining to the specific phenomena under investigation (White, 2000).

The inherent low signal-to-noise ratio characteristic of financial data, compounded by survival bias in historical datasets and the overfitting of models during backtesting procedures, significantly complicates the construction of robust market environments and benchmarks for financial reinforcement learning (FinRL) (FinRL-Meta kütüphanesi). Consequently, the performance of Deep Reinforcement Learning (DRL) strategies in real-world market conditions can be substantially diminished (FinRL-Meta kütüphanesi). Furthermore, manipulative practices, such as wash trading, wherein investors simultaneously buy and sell the same assets to artificially inflate market activity, can distort prices, trading volume, and volatility, thereby eroding investor confidence (Çalışma). Research suggests that wash trading is rampant on unregulated exchanges, inflating reported volumes by over 70% (Çalışma). This form of manipulation can artificially enhance an exchange's ranking, influence short-term price distributions, and is observed more frequently on newly established exchanges (Çalışma).

To address the challenges posed by data snooping, White (2000) introduced the Reality Check for Data Snooping, a notable contribution to the field that facilitates the comparison of a benchmark model against multiple competing models. This approach effectively controls the overall error rate when comparing a multitude of models, acknowledging that the probability of selecting an alternative model by chance increases proportionally with the number of competitors (White, 2000). White's Reality Check provides a method for controlling the probability of incorrectly rejecting a true null hypothesis (White, 2000). While White's Reality Check effectively addresses scenarios where parameter estimation error is negligible, Corradi and Swanson (2006a, 2007a) have developed bootstrap procedures that explicitly account for the contribution of parameter estimation errors within rolling or recursive forecasting schemes.



### Transaction Cost Modeling in Cryptocurrency Backtesting
## Kripto Para Birimi Geriye Dönük Testlerinde İşlem Maliyeti Modellemesi

Kripto para birimi alım satım stratejilerinin geriye dönük test metodolojilerinde işlem maliyetlerinin modellenmesi, stratejilerin gerçek dünya performansının doğru bir şekilde değerlendirilmesi için hayati bir öneme sahiptir. İşlem maliyetleri, alım satım stratejilerinin karlılığını önemli ölçüde etkileyebilir ve bu nedenle geriye dönük test süreçlerinde titizlikle hesaba katılmalıdır.

### Doğrusal İşlem Maliyetleri

Doğrusal işlem maliyetleri, alım satım hacmiyle orantılı olarak artan maliyetlerdir. Bu tür maliyetler, matematiksel olarak şu şekilde modellenebilir: 1Tu= 0 kısıtlaması yerine 1Tu+κTbuyu++κTsellu−= 0 denklemi kullanılır (Author, Year). Burada κsell satış işlem maliyet oranları vektörünü, κbuy ise alış işlem maliyet oranları vektörünü temsil etmektedir. u+ ve u− sırasıyla u'nun pozitif ve negatif kısımlarını ifade eder. −1Tut, satışlardan elde edilen toplam brüt gelir ile alımlar için ödenen toplam brüt tutar arasındaki farkı temsil eder ve bu fark, κTbuyu+ (alış işlemlerinin toplam işlem maliyeti) ve κTsellu− (satış işlemlerinin toplam işlem maliyeti) toplamına eşittir (Author, Year). İşlem maliyetlerinin varlığı, optimal politika hesaplamasını önemli ölçüde karmaşık hale getirmektedir (Author, Year).

### Dışbükey İşlem Maliyetleri ve Portföy Optimizasyonu

Portföy optimizasyonu modelleri, riskten kaçınmayı, portföy kısıtlamalarını ve dışbükey işlem maliyetlerini dikkate almalıdır (Author, Year). İşlem maliyetlerini göz ardı eden bir "maliyet körü" stratejisi, diğer buluşsal yöntemlerin performansını değerlendirmek için bir kıyaslama noktası olarak kabul edilebilir (Author, Year). "Tek adımlı" strateji, dinamik programlama yinelemesini, devam değerini işlem maliyetlerini göz ardı eden modelin değer fonksiyonu olarak alarak yaklaşık olarak değerlendirir; işlem maliyetleri yalnızca mevcut dönemde dikkate alınır (Author, Year). "Yuvarlanan al ve tut" stratejisi, her dönemde, sabit bir ufukta daha fazla ticaret fırsatı olmayacağı basitleştirici varsayımıyla işlem maliyetleriyle bir optimizasyon problemi çözer; ufkun sonundaki devam değeri yine işlem maliyetlerini göz ardı eden modelin değer fonksiyonu olarak alınır (Author, Year). İşlem maliyetleri ile portföy optimizasyonu, stokastik dinamik bir program olarak formüle edilebilir (Author, Year). İşlem maliyetleri olmadan, optimal yatırımlar tipik olarak yatırımcının servetine bağlıdır, ancak yatırımcının varlık pozisyonlarına bağlı değildir. Bununla birlikte, işlem maliyetleriyle, optimal yatırımlar yatırımcının ilk varlık pozisyonlarına bağlıdır ve durum uzayının boyutu, dikkate alınan varlıkların sayısı kadar büyüktür (Author, Year). Çözümler, işlem maliyetlerinin olmamasına büyük ölçüde dayanır. Uygulamada, işlemler maliyetlidir ve sürekli yeniden dengeleme oldukça pahalı olabilir (Author, Year). Sürekli yeniden dengeleme, işlem maliyetleri nedeniyle pahalı olabilir (Author, Year). Model, öngörülebilir getirileri ve dışbükey işlem maliyetlerini dikkate alır (Author, Year). Buluşsal yöntemler, optimal bir ticaret stratejisiyle performansta üst sınırlar ile tamamlanır (Author, Year). Sınırlar, gelecekteki getiriler hakkında mükemmel bilgiye sahip olan ancak bu ön bilgiyi kullandığı için cezalandırılan bir yatırımcıyı dikkate alarak verilir (Author, Year). Hem buluşsal yöntemler hem de ikili sınırlar Monte Carlo simülasyonu kullanılarak eşzamanlı olarak değerlendirilebilir (Author, Year). Buluşsal yöntemler ve ikili sınırlar, farklı fayda fonksiyonları, farklı işlem maliyeti biçimleri (dışbükey olmaları koşuluyla), farklı portföy kısıtlamaları ve farklı getiri modelleriyle ilgili sorunlara uyarlanabilir (Author, Year).

### Yürütme Zamanlaması ve İşlem Maliyetleri

İşlem maliyetlerinin değerlendirilmesinde yürütme zamanlamasının önemi vurgulanmaktadır (Author, Year). Hızlı yürütülen emirler daha yüksek maliyetlere yol açarken, daha kademeli işlemler varlığın değerinin daha uzun sürelerde değişebileceği için daha yüksek risk taşır (Author, Year). Farklı emir yürütme yaklaşımlarıyla ilişkili beklenen maliyeti ve riski ölçmek ve modellemek için bir veri seti kullanılır (Author, Year). İşlem maliyeti ölçüsü, emir gönderildiği andaki fiyatı bir kıyaslama fiyatı olarak alır (Author, Year). İşlem maliyeti, işlem fiyatı ile kıyaslama fiyatı arasındaki farkın ağırlıklı toplamıdır; ağırlıklar ise işlem gören miktarlardır (Author, Year). İşlem maliyetinin hem ortalaması hem de varyansı oluşturulur (Author, Year). İşlem maliyeti, yerel etkileri yakalayan geleneksel işlem maliyeti ölçüleriyle yakından ilişkili olan iki bileşene ayrılabilir (Author, Year). Yüksek beklenen maliyet ve düşük risk ile düşük beklenen maliyet ve yüksek risk arasında bir denge vardır (Author, Year). Piyasa koşulları ve emrin özelliklerine bağlı olarak değişen bir risk/maliyet dengesi sunulmaktadır (Author, Year). Veriler, emir gönderilme zamanı ile emri doldururken yapılan işlemlerin zamanları, fiyatları ve miktarları hakkında bilgiler içermektedir (Author, Year).

### Orantılı İşlem Maliyetleri ve Koşullu Talep Hedging

Orantılı işlem maliyetleri altında sürekli zamanlı bir modelde, herhangi bir koşullu talebi hedge etmek için gereken minimum başlangıç serveti için bir formül türetilmektedir (Author, Year). Ayrıca, terminal servetten elde edilen faydayı maksimize etme portföy optimizasyon probleminin optimal çözümünün varlığı kanıtlanmaktadır (Author, Year). Model, banka hesabı ve hisse senedi olmak üzere iki varlık içermektedir ve işlem maliyetleri, bankadan hisse senedine veya tersi yönde yapılan transferler için orantılıdır (Author, Year). Bir ticaret stratejisi, bu transferleri temsil eden uyarlanmış süreçler çiftidir (Author, Year). Bir koşullu talep, terminal zamanda banka hesabındaki ve hisse senedindeki hedef pozisyonlardır (Author, Year). Bir ticaret stratejisi, başlangıç pozisyonlarıyla başlayarak, terminal zamanda bu hedef pozisyonları karşılayacak kadar varlık sağlaması durumunda talebi hedge eder (Author, Year).



## Optimal Indicator Combinations for Cryptocurrency Exchanges

### Identifying Best Performing Indicator Combinations for Bitcoin (BTC)
## Bitcoin (BTC) İçin Optimal Gösterge Kombinasyonlarının Belirlenmesi

Kripto para piyasaları, özellikle Bitcoin (BTC), son yıllarda artan yatırımcı ilgisi ve piyasa değeri ile önemli bir yer edinmiştir. Bu durum, Bitcoin fiyatlarının yüksek frekanslı trend tahminlerine yönelik akademik araştırmaları da beraberinde getirmiştir. Bu bağlamda, evrişimsel sinir ağları (CNN) ve uzun kısa süreli bellek (LSTM) ağları gibi derin öğrenme teknikleri, dakika seviyesindeki teknik göstergeler kullanılarak uygulanmaktadır (Ji, Kim & Im, Tarih Belirtilmemiş). Bu yaklaşımların temel amacı, Bitcoin'leri pasif olarak elde tutma stratejisine kıyasla daha yüksek getiri potansiyeli sunan ticaret stratejileri geliştirmektir.

Alonso-Monsalve ve diğerleri (Tarih Belirtilmemiş), dakika seviyesindeki Bitcoin fiyatlarından türetilen 18 teknik göstergeyi kullanarak, Bitcoin, Dash, Ether, Litecoin, Monero ve Ripple gibi önde gelen kripto para birimlerinin fiyat değişimlerini tahmin etmek amacıyla CNN, hibrit CNN-LSTM ağı, çok katmanlı algılayıcı (MLP) ve radyal bazlı fonksiyon (RBF) sinir ağlarını değerlendirmişlerdir. Araştırmaları, hibrit CNN-LSTM ağının en iyi performansı sergilediğini ve Monero ve Dash'ın fiyat değişimlerini tahmin etmede sırasıyla %80 ve %74'e varan test doğruluğuna ulaştığını göstermiştir. Mevcut çalışmalarda da benzer şekilde hibrit CNN-LSTM modelleri geliştirilmiş ve bu modellerin teknik göstergelerden anlamlı sinyaller çıkarma kapasitesine sahip olduğu ortaya konmuştur.

Bu modellerde kullanılan girdi değişkenleri, Alonso-Monsalve ve diğerlerinin (Tarih Belirtilmemiş) çalışmalarına paralel olarak, bazı eklemelerle birlikte 30 teknik göstergeyi içermektedir. Bu göstergeler arasında Momentum (MOM), MOM ret, SMA ret, WMA ret, Göreceli Güç Endeksi (RSI), Stokastik Osilatör (SK), Standart Sapma (SD10), Larry Williams R% (LWR), Emtia Kanalı Endeksi (CCI), Hareketli Ortalama Yakınsama Iraksama (MACD), ADOSC Binance ve ADOSC all bulunmaktadır. Teknik göstergelerin hesaplanması, momentum, son fiyat seviyeleri arasındaki ilişkiler, aşırı alım ve aşırı satım koşulları ve genel birikim ve dağılım gibi fiyat dinamiklerinin önemli özelliklerini ortaya çıkaran bir transfer öğrenme süreci olarak değerlendirilebilir.

Model mimarisi, CNN ve LSTM olmak üzere iki temel bileşenden oluşmaktadır. CNN, bitişik veriler arasındaki ilişkileri etkin bir şekilde kullanma ve yüksek frekanslı verilerin işlenmesini hızlandırma yeteneği nedeniyle tercih edilmiştir. LSTM ağları ise, Bitcoin verileri arasındaki sıralı ilişkileri daha iyi modellemek ve uzun vadeli bağımlılıkları yakalamak amacıyla entegre edilmiştir. Bu entegrasyon, modelin piyasa dinamiklerini daha kapsamlı bir şekilde anlamasına ve daha doğru tahminler yapmasına olanak sağlamaktadır.



### Identifying Best Performing Indicator Combinations for Ethereum (ETH)
**Ethereum (ETH) İçin Optimal Gösterge Kombinasyonlarının Belirlenmesine İlişkin Literatürdeki Boşluklar**

Kripto para borsaları için optimal gösterge kombinasyonlarının belirlenmesi, özellikle de Ethereum (ETH) için en iyi performansı gösteren kombinasyonların tespiti, mevcut akademik literatürde sınırlı bir şekilde ele alınmaktadır. Mevcut çalışmaların büyük bir bölümü, bu spesifik konuya doğrudan odaklanmaktan ziyade, blok zincir teknolojisinin temel prensiplerine (Author, Year) veya kombinatoryal test kümelerinde arızaya neden olan kombinasyonların belirlenmesine (Author, Year) yoğunlaşmaktadır. Niteliksel Karşılaştırmalı Analiz (QCA) yönteminin strateji ve organizasyon araştırmalarındaki en iyi uygulamalarını inceleyen çalışmalar (Author, Year) bulunmakla birlikte, bu çalışmalar da ETH ile ilgili gösterge kombinasyonları hakkında doğrudan bilgi sağlamamaktadır.

Bununla birlikte, bazı araştırmalar kripto para piyasasının zayıf formda verimliliğini analiz etmeye yöneliktir. Örneğin, Ethereum (ETH) de dahil olmak üzere beş büyük kripto para biriminin (Bitcoin, Ethereum, XRP, Cardano ve Binance Coin) zayıf formda piyasa verimliliğini inceleyen çalışmalar, kripto para piyasasının zayıf formda verimli olmadığı sonucuna varmıştır (Author, Year). Ayrıca, yükselen araştırma alanlarını belirlemek amacıyla farklı göstergeleri birleştiren karma modeller de mevcuttur. Bu modeller, belirli kelimelerin sıklığındaki ani artışlar, yeni yazarların ortaya çıkan bir araştırma alanına yönelme sayısı ve hızı, ve atıfta bulunulan referansların disiplinlerarasılığındaki değişimler gibi çeşitli göstergeleri bir araya getirmektedir (Author, Year). Bu türden modeller, kripto para piyasalarındaki optimal gösterge kombinasyonlarını belirlemek için potansiyel bir çerçeve sunabilir; ancak bu alanda daha kapsamlı ve derinlemesine araştırmalara ihtiyaç duyulmaktadır.



### Identifying Best Performing Indicator Combinations for Altcoins
### Altcoin Piyasasında Madencilik ve Spekülasyonun Karlılığı

Bitcoin'in başarısını takiben ortaya çıkan altcoin'ler, yatırımcılar tarafından giderek artan bir şekilde spekülatif yatırım araçları olarak değerlendirilmektedir (Author, Year). Bu durum, altcoin piyasasının, kar elde etme motivasyonuyla hareket eden madenciler ve spekülatörler gibi çeşitli yatırımcı gruplarını cezbetmesine neden olmaktadır (Author, Year). Madenciler, karmaşık algoritmik problemleri çözerek (hash çatışmaları bularak) yeni dijital varlıklar üretirken, spekülatörler ise piyasadaki fiyat dalgalanmalarından faydalanarak kar elde etmeyi amaçlamaktadır (Author, Year). Yatırımcılar, altcoin madenciliği yaparak veya doğrudan piyasadan satın alarak bu ekosisteme dahil olabilirler (Author, Year). Madencilik faaliyetlerinde bulunanlar, elde ettikleri coin'lerin değer kazanması durumunda bunları satarak spekülasyon yoluyla ek gelir elde etme potansiyeline de sahiptirler (Author, Year).

Altcoin piyasasının dinamik yapısı göz önüne alındığında, bir çalışmada 18 farklı altcoin'in madencilik ve spekülasyon yoluyla potansiyel karlılığı detaylı bir şekilde incelenmiştir (Author, Year). Madencilik maliyetinin hesaplanmasında, fırsat maliyeti kavramı temel bir unsur olarak kullanılmıştır (Author, Year). Fırsat maliyeti, bir altcoin'i madencilik yapmanın, daha yerleşik ve istikrarlı bir kripto para birimine (örneğin Bitcoin) kıyasla maliyetini ifade etmektedir (Author, Year). Bu bağlamda, her bir dolarlık yatırım için, piyasaya giriş zamanlaması ve pozisyon tutma süresi gibi çeşitli parametreler dikkate alınarak potansiyel getiriler ayrıntılı olarak hesaplanmıştır (Author, Year).

Elde edilen bulgular, madencilerin bir altcoin'in borsalarda listelenmesini takiben mümkün olan en kısa sürede madencilik faaliyetlerine başlamaları durumunda, daha sonraki dönemlerde madencilik yapanlara kıyasla daha yüksek potansiyel getiri elde etme eğiliminde olduklarını göstermektedir (Author, Year). Buna karşılık, spekülatörlerin bir altcoin'i borsalarda listelendikten kısa bir süre sonra satın almaları durumunda, daha sonraki bir tarihte satın alanlara göre daha düşük getiri elde etme olasılığı daha yüksektir ve aynı zaman diliminde madencilere kıyasla daha düşük performans gösterme eğilimindedirler (Author, Year). Bu durum, altcoin piyasasında erken dönem madenciliğin, spekülasyona kıyasla daha avantajlı olabileceğine işaret etmektedir (Author, Year).



### Performance Comparison of Indicator Combinations Across Different Cryptocurrencies
## Kripto Para Birimlerinde Gösterge Kombinasyonlarının Performans Karşılaştırması

Kripto para piyasalarının dinamik yapısı ve farklı kripto para birimlerinin sergilediği özgün davranışlar, optimal gösterge kombinasyonlarının belirlenmesi sürecinde dikkate alınması gereken kritik faktörlerdir. Bu bağlamda, mevcut literatürde çeşitli metodolojik yaklaşımlar ve ampirik bulgular mevcuttur.

Bir çalışma, Bitcoin ve Ethereum'un fiyat hareketleri ile işlem hacmi arasındaki ilişkiyi farklı kripto para borsalarında incelemiş ve bu ilişkinin tahmini için parametrik olmayan bir nedensellik-kantillerde yöntemi uygulamıştır (Author, Year). Bu araştırma, birden fazla borsadan elde edilen verileri ve daha geniş bir zaman dilimini kapsayarak mevcut literatüre katkıda bulunmuş ve söz konusu metodolojiyi diğer kripto para birimlerine de uygulamıştır. Elde edilen bulgular, Bitcoin işlem hacminin, piyasa davranışına bağlı olarak getirileri ve oynaklığı etkilediğini göstermektedir. Ayrıca, çalışmanın eklerinde diğer kripto para birimlerine ilişkin ampirik sonuçlar da detaylı bir şekilde tartışılmıştır (Author, Year).

Başka bir araştırma, kripto para birimlerini, kullanıcı katılımını yönlendiren ağ etkileri ve token fiyatının tarafsız olmaması ile birlikte, token piyasasının çökmesine neden olabilecek merkezi olmayan bir dijital platform tarafından kullanılan fayda token'ları olarak modellemektedir (Author, Year). Token'ın yeniden ticarete konu olmasının, kullanıcı iyimserliğinden yararlanarak daha genç platformlarda bu çökme riskini azalttığı, ancak spekülatörlerin duygu odaklı ticaretinin kullanıcıları dışlaması durumunda bu kırılganlığı kötüleştirdiği gösterilmektedir. Esnek token ihracı bu kırılganlığı azaltır, ancak madenciler tarafından yapılan stratejik saldırılar, kullanıcıların gelecekteki kayıplara ilişkin beklentileri token'ın yeniden satış değerini düşürdüğü için bunu daha da kötüleştirir. Geliştirilen model, farklı kripto para birimlerindeki platform performansını sistematik bir şekilde karakterize etme potansiyeline sahiptir (Author, Year).

Kripto para piyasalarında, borsalar arasında önemli ve tekrarlayan arbitraj fırsatlarının varlığı da gözlemlenmektedir (Author, Year). Bu fiyat farklılıklarının, ülke içindekilere kıyasla ülkeler arasında daha belirgin olduğu ve kripto para birimleri arasında daha az olduğu tespit edilmiştir. Bu durum, arbitraj sermayesinin hareketinde sermaye kontrollerinin önemini vurgulamaktadır. Ülkeler arasındaki fiyat farklılıkları birlikte hareket etmekte ve Bitcoin'in değer kazandığı dönemlerde daha da belirginleşmektedir. ABD Bitcoin fiyatı üzerinde daha yüksek primi olan ülkelerde, Bitcoin değerlendiğinde arbitraj sapmalarının genişlediği gözlemlenmiştir. Bu çalışma, 34 borsa ve 19 ülke için yüksek frekanslı (tick) verilerini kullanmaktadır (Author, Year). Elde edilen bulgulara göre, ABD ve Kore arasındaki günlük ortalama fiyat oranının Aralık 2017'den Şubat 2018'in başına kadar %15'in üzerinde olduğu ve bazı günlerde %40'a ulaştığı belirtilmektedir. Japonya ve ABD arasındaki ortalama fiyat farkı yaklaşık %10, ABD ile Avrupa arasındaki ise yaklaşık %3 olarak tespit edilmiştir. ABD ve Avrupa dışındaki ülkelerde, Bitcoin genellikle ABD'ye göre primli işlem görmekte ve neredeyse hiçbir zaman ABD'nin altındaki bir fiyattan işlem görmemektedir. Fiyat farklılıkları, Bitcoin fiyatlarının özellikle hızlı değerlendiği dönemlerde ortaya çıkmaktadır. Ülkelerin Bitcoin fiyatının ABD'ye göre sapmaları, ABD'deki Bitcoin'in log fiyatı ile trend bileşeni arasındaki farka göre regresyona tabi tutulmuştur. ABD'deki Bitcoin fiyatı, Bitcoin'in küresel piyasa fiyatı için iyi bir gösterge olarak kabul edilmektedir. ABD Bitcoin fiyatı üzerinde daha yüksek primi olan ülkeler, daha yüksek bir Bitcoin betasına sahiptir. Bu nedenle, bu ülkeler, ABD'de alım baskısı arttığında arbitraj sapmalarını genişletmede daha güçlü tepki vermektedir (Author, Year).

Son olarak, bir çalışma Şubat 2014 - Eylül 2018 döneminde, ana kripto para birimleri ve geleneksel para birimleri arasındaki oynaklık bağlantısını incelemiştir (Author, Year). İncelenen sekiz kripto para birimi ve geleneksel para birimi arasındaki şokların, toplam varyansın %34,43'ünü açıkladığı bulunmuştur. Oynaklık bağlantısının zamanla değiştiği ve ekonomik ve finansal istikrarsızlık dönemlerinde arttığı gözlemlenmiştir. Geleneksel para birimleri ve kripto para birimleri blokları arasında hafif net oynaklık yayılması dönemleri ile çoğunlukla bağlantısız olduğu bulunmuştur. Finansal piyasa değişkenlerinin geleneksel para birimleri içindeki toplam bağlantının ana itici güçleri olduğu, kripto para birimine özgü değişkenlerin ise geleneksel para birimleri içindeki toplam bağlantının ve iş döngüsü ile kripto para birimine özgü değişkenlerin bir kombinasyonunun bloklar arasındaki yönlü oynaklık bağlantısını açıkladığı tespit edilmiştir (Author, Year).

Bu çalışmaların genelinde, kripto para piyasalarının karmaşıklığı ve farklı kripto para birimlerinin davranışlarını anlamak için çeşitli analitik yaklaşımların gerekliliği vurgulanmaktadır. Optimal gösterge kombinasyonlarının belirlenmesi, bu farklılıkların dikkate alınmasını ve piyasa koşullarına adaptasyon sağlanmasını gerektiren çok boyutlu bir süreçtir.



### Impact of Exchange Characteristics on Indicator Combination Performance
## Kripto Para Borsalarında Teknik Göstergelerin Rolü ve Borsa Özelliklerinin Gösterge Kombinasyonu Performansına Etkisi

Teknik analiz, potansiyel piyasa hareketlerini belirlemek amacıyla geçmiş fiyat verilerini kullanarak çeşitli göstergeler üretmektedir (Author, Year). Bu göstergeler, piyasa eğilimlerini değerlendirmek için hareketli ortalamaları (MA) içerirken, momentum osilatörleri ve göreli güç endeksleri (RSI) gibi araçlar, bir varlığın aşırı alım veya aşırı satım koşullarını değerlendirmeye yardımcı olmaktadır (Author, Year). Göstergeler, genel olarak öncü ve gecikmeli olmak üzere iki ana kategoriye ayrılmaktadır. Öncü göstergeler, piyasa hareketlerine yansıyan ekonomik değişikliklere odaklanırken, gecikmeli göstergeler hisse senedi fiyatlarındaki değişimleri takip etmeyi amaçlamaktadır (Author, Year). Dolayısıyla, yatırımcılar bir menkul kıymetin geçmiş fiyat eğilimlerini değerlendirmek istediklerinde gecikmeli göstergelerden faydalanabilmektedirler (Author, Year).

Gecikmeli teknik göstergelerin (örneğin, Üstel Hareketli Ortalama (EMA) ve Ağırlıklı Hareketli Ortalama (WMA)) tek başına kullanımı, hisse senedi tahmininin doğruluğunu artırabilmektedir (Author, Year). Hareketli ortalama (MA), belirli bir zaman dilimindeki bir varlığın ortalama fiyatını temsil etmektedir (Author, Year). Üstel Hareketli Ortalama (EMA), son verilere daha fazla ağırlık vererek hesaplanmaktadır (Author, Year). Ağırlıklı Hareketli Ortalama (WMA) ise, varlık kapanış fiyatlarının ağırlıklı ortalamasını ifade etmekte ve Basit Hareketli Ortalama'ya (SMA) kıyasla daha az gecikme sunmaktadır (Author, Year). Ayrıca, piyasa gürültüsünü ve oynaklığını dikkate alan Kaufman Uyarlanabilir Hareketli Ortalaması (KAMA) gibi daha karmaşık göstergeler de mevcuttur (Author, Year). Farklı göstergelerin kombinasyonu, tahmin performansını daha da artırabilmektedir (Author, Year). Özellikle piyasada yatay bir seyir izlendiği durumlarda (belirgin bir yükseliş veya düşüş trendinin olmadığı zamanlarda), öncü göstergelerin daha iyi performans gösterdiği gözlemlenmektedir (Author, Year).



### Adaptive Indicator Combinations for Changing Market Conditions
### Değişen Piyasa Koşullarına Uyarlanabilir Gösterge Kombinasyonları

Kripto para piyasalarının doğasında bulunan dinamiklik, statik gösterge kombinasyonlarının zaman içindeki etkinliğini azaltma potansiyeline sahiptir. Bu durum, değişen piyasa koşullarına etkin bir şekilde uyum sağlayabilen adaptif stratejilerin geliştirilmesinin önemini vurgulamaktadır. İnsan davranışının evrim ve çevresel faktörler tarafından şekillendirildiği (Anonim, Yıl) göz önünde bulundurulduğunda, piyasaların hem bireysel hem de grup seviyelerinde biyolojik bir perspektifle incelenmesi gerekmektedir. Rekabet, adaptasyonu ve inovasyonu teşvik ederken, doğal seçilim piyasa ekolojisini şekillendirmekte ve evrim piyasa dinamiklerini belirlemektedir (Anonim, Yıl).

Geleneksel finansal modellerin sınırlılıkları dikkate alındığında (Anonim, Yıl), dinamik bir ortamın dinamik finansal politikalar gerektirdiği aşikardır (Anonim, Yıl). Bu bağlamda, "Uyarlanabilir Piyasalar Hipotezi" (AMH) (Anonim, Yıl), piyasaların her zaman verimli olmadığını, ancak genellikle rekabetçi ve uyarlanabilir olduğunu ve ortam ile yatırımcı popülasyonu zamanla değiştikçe verimlilik derecelerinin de değiştiğini öne sürmektedir (Anonim, Yıl). AMH, piyasaların evrimsel biyoloji perspektifinden incelenmesini önermekte ve değişen piyasa koşullarına nasıl yanıt verileceğine dair kavramsal bir çerçeve sunmaktadır (Anonim, Yıl). Zira, risk/ödül ilişkisi her zaman ve her koşulda geçerli olmayabilir (Anonim, Yıl).

Bu hipotez, akıllı fakat yanılgıya düşebilen yatırımcıların değişen ekonomik ortamlardan öğrendiği ve bu ortamlara uyum sağladığı temel fikrine dayanmaktadır (Anonim, Yıl). Güçlü duygusal uyaranlar hızlı tepkilere yol açarken, hafıza ve tahminleme temelli öğrenme süreçleri daha yavaş ilerlemektedir (Anonim, Yıl). Dolayısıyla, piyasa koşulları değiştikçe uyum yeteneğini artırmak ve adaptif öğrenme algoritmalarını kullanmak, kavram kayması (concept drift) sorununu ele almak açısından kritik bir öneme sahiptir (Anonim, Yıl).



## Machine Learning and AI in Cryptocurrency Trading Indicator Selection

### Using Machine Learning to Optimize Indicator Weights
## Makine Öğrenimi ile Gösterge Ağırlıklarının Optimizasyonu

Kripto para birimi ticaretinde teknik göstergelerin başarısı, büyük ölçüde bu göstergelere atanan ağırlıkların doğruluğuna bağlıdır. Makine öğrenimi algoritmaları, bu ağırlıkları optimize etmek için etkili bir metodoloji sunmaktadır. Bu bağlamda, makine öğrenimi hedefleri, modelin tahmin performansına uygulanan "oran kısıtlamaları" olarak formüle edilebilir (241.pdf). Bu yaklaşım, eğitim sürecini kısıtlı bir optimizasyon problemine dönüştürmektedir. Örneğin, bir ikili sınıflandırıcının, örneklerin en az %80'inde pozitif tahminler yapması beklenebilir (241.pdf).

Kısıtlamalarla eğitim, çeşitli zorlukları beraberinde getirmektedir. İlk olarak, sinir ağları gibi doğrusal olmayan fonksiyon sınıfları için, amaç ve kısıtlama fonksiyonları, dışbükey kayıp fonksiyonları kullanıldığında dahi dışbükey olmayabilir (242.pdf). İkinci olarak, oran kısıtlamaları, pozitif ve negatif sınıflandırma oranlarının doğrusal kombinasyonlarıdır ve bu nedenle gösterge fonksiyonlarından (0-1 kayıpları) oluşurlar. Bu durum, neredeyse her yerde sıfır gradyanlara yol açarak optimizasyonu zorlaştırmaktadır (242.pdf).

Literatürde, kısıtlı optimizasyon problemlerine Lagrange çarpanları yaklaşımının, dışbükey olmayan (non-convex) problemler için yetersiz kalabileceği belirtilmektedir (245.pdf). Ayrıca, kısıtlamalar türevlenebilir değilse, Lagrange fonksiyonunu gradyan tabanlı yöntemlerle optimize etmek mümkün değildir (245.pdf). Bu sorunların üstesinden gelmek amacıyla, yeni "proxy-Lagrangian" formülasyonları önerilmektedir (246.pdf). Bu yaklaşımlar, bir optimizasyon oracle'ına erişim varsayılarak, kısıtlı optimizasyon problemine yaklaşık olarak optimal ve uygulanabilir bir çözüm olan yarı kaba ilişkili bir dengeyi çözen iki oyunculu sıfır toplamlı olmayan bir oyun oynayarak stokastik bir sınıflandırıcı üretmeyi amaçlamaktadır (246.pdf).

Alternatif bir yaklaşım, veri noktaları arasındaki mesafeyi tanımlayan bir mesafe fonksiyonu kullanarak verilerin sınıflandırılmasını içermektedir (247.pdf). Bu mesafe fonksiyonları genellikle ağırlıklar veya maliyetler kullanılarak tanımlanır ve bu ağırlıkların anlamlı bir şekilde ayarlanması kritik öneme sahiptir (247.pdf). Bu bağlamda, mevcut çalışmalar, bu ağırlıkları veri kullanarak öğrenen bir çerçeve sunmaktadır (248.pdf). Çerçevenin çalışma zamanını iyileştirmek için paralelleştirme teknikleri uygulanmış ve ağırlıkların nasıl optimize edileceğine dair sonuçlar sunulmuştur (248.pdf). Bu çerçeve, iki aşamada çalışmaktadır: İlk aşamada, bir mesafe matrisi hesaplanır; burada (i,j) girdisi, xi ve xj veri noktaları arasındaki mesafedir (249.pdf). İkinci aşamada, bu mesafe matrisi ağırlık kümesini optimize etmek için kullanılır (249.pdf). Mesafe matrisinin hesaplanmasının çalışma zamanını hızlandırmak için paralelleştirme tanıtılmıştır ve ağırlıkları optimize etmenin bir yolu hakkında sonuçlar sunulmaktadır (250.pdf).



### Applying Deep Learning for Cryptocurrency Price Prediction
## Kripto Para Fiyat Tahmininde Derin Öğrenme Uygulamaları

Kripto para birimlerinin, özellikle Bitcoin'in 2017'deki önemli fiyat artışıyla birlikte artan popülaritesi, yatırım stratejileri geliştirmek amacıyla yüksek frekanslı fiyat tahminlerinin önemini vurgulamıştır. Bu bağlamda, derin öğrenme algoritmaları, kripto para fiyat tahmininde potansiyel çözümler sunmaktadır. Bu bölümde, derin öğrenme yöntemlerinin kripto para fiyat tahminindeki uygulamaları ve ilgili araştırmalar detaylı bir şekilde incelenecektir.

### Derin Öğrenme Algoritmalarının Kripto Para Fiyat Tahminine Uygulanması

Derin öğrenme algoritmalarının kripto para birimlerinin yüksek frekanslı trend tahminindeki etkinliği çeşitli çalışmalarda değerlendirilmiştir. Örneğin, Bitcoin getirilerini tahmin etmek amacıyla Derin Sinir Ağları (DNN), Uzun Kısa Süreli Bellek (LSTM), Evrişimsel Sinir Ağları (CNN) ve Tekrarlayan Sinir Ağları (RNN) gibi derin öğrenme algoritmaları kullanılmıştır (Ji et al., tarih belirtilmemiş). Ancak, bu çalışmada farklı algoritmalar arasında istatistiksel olarak anlamlı bir performans farkı tespit edilememiştir. Diğer bir çalışmada ise, Alonso-Monsalve et al. (tarih belirtilmemiş), dakika seviyesindeki Bitcoin fiyatlarından türetilen 18 teknik göstergeyi kullanarak CNN, hibrit CNN-LSTM ağı, Çok Katmanlı Algılayıcı (MLP) ve Radyal Tabanlı Fonksiyon (RBF) sinir ağlarını, Bitcoin, Dash, Ether, Litecoin, Monero ve Ripple gibi altı popüler kripto para biriminin fiyat değişikliklerini tahmin etmek için kullanmışlardır. Bu araştırmada, hibrit CNN-LSTM ağının en iyi performansı sergilediği ve Monero ve Dash'in fiyat değişikliklerini tahmin etmede %80 ve %74'e varan test doğruluklarına ulaştığı belirtilmiştir.

### CNN-LSTM Hibrit Modelinin Kullanımı

Bu alandaki bir diğer çalışma, Bitcoin fiyatlarının tek adımlı yüksek frekanslı trend tahminlerini gerçekleştirmek amacıyla CNN ve LSTM ağlarının derin öğrenme tekniklerini sınıflandırma algoritmaları olarak kullanmıştır (yazar belirtilmemiş, tarih belirtilmemiş). Bu modelin temel amacı, Binance borsasında işlem gören Bitcoin'lerin dakika seviyesindeki fiyat değişikliklerini tahmin etmek ve varlıkları pasif olarak tutma stratejisinden daha iyi sonuçlar verebilecek yatırım stratejileri geliştirmektir. Modelin girdileri, dakika seviyesindeki açılış, kapanış, yüksek ve düşük fiyatlar ile işlem hacminden oluşmaktadır.

Modelin mimarisi, bitişik veriler arasındaki ilişkilerden faydalanma ve yüksek frekanslı verinin işlenmesini hızlandırma yeteneği nedeniyle CNN'yi içermektedir. LSTM ağları ise, teknik göstergelerin zaman serisi verileri olan Bitcoin verileri arasındaki sıralı ilişkileri modellemek için kullanılmaktadır. CNN katmanlarının çıktıları, girdi olarak kullanılan iki derin LSTM katmanı ile önceden oluşturulmuş CNN mimarisine entegre edilmiştir.

### Veri Seti ve Model Konfigürasyonu

Söz konusu çalışmada, 8 Temmuz 2020'den 11 Şubat 2021'e kadar olan dakika seviyesindeki Bitcoin fiyatları ve hacimleri toplanarak toplamda 313.327 veri noktası elde edilmiştir. Fiyat değişikliği etiketleri (0 ve 1), sırasıyla fiyattaki düşüşü ve artışı temsil etmektedir. Veri kümesinin %80'i eğitim seti olarak kullanılırken, geri kalan %20'lik kısım geliştirme ve test setlerine ayrılmıştır. Girdiler, 30 teknik göstergeyi hesaplamak için kullanılmıştır. CNN katmanları 40x30 boyutunda girdi almakta ve filtrelerden geçtikten sonra 28x10 boyutunda çıktı üretmektedir. LSTM mimarisi ise, 2 katmanlı derin bir yapıya sahip olup, her katmanın çıktı birimi 100 olarak belirlenmiştir.

### Alternatif Yaklaşımlar ve Gelecek Araştırmalar

Kripto para fiyat tahmininde RNN modellerinin uygulanmasını inceleyen bir başka çalışmada, Basit RNN, LSTM ve GRU modelleri karşılaştırılmış ve Google Trendleri verilerinin eklenmesinin tahmin doğruluğunu artırıp artırmadığı değerlendirilmiştir (yazar belirtilmemiş, tarih belirtilmemiş). Elde edilen sonuçlar, test edilen RNN modelleri arasında belirgin bir performans farkı olmadığını ve Google Trendleri verilerinin eklenmesinin modelin tahmin doğruluğunu önemli ölçüde iyileştirmediğini göstermiştir.

Gelecekteki araştırmalar için, kayan pencere çapraz doğrulamasının uygulanması ve ek özellikler kullanılarak CNN ve CNN-LSTM hibrit modelinin yeniden kalibre edilmesi ve geliştirilmesi planlanmaktadır (yazar belirtilmemiş, tarih belirtilmemiş).

### Sonuç

Derin öğrenme algoritmaları, kripto para fiyat tahmininde umut vadeden sonuçlar sunmaktadır. Özellikle CNN ve LSTM tabanlı hibrit modeller, yüksek frekanslı veriyi analiz etme ve zaman serisi ilişkilerini yakalama yetenekleri sayesinde etkili sonuçlar ortaya koymaktadır. Bununla birlikte, farklı algoritmaların ve veri kaynaklarının kombinasyonlarının sistematik olarak araştırılması ve modellerin sürekli olarak güncellenmesi, daha doğru ve güvenilir tahminler elde etmek için kritik öneme sahiptir.



### AI-Driven Indicator Selection for Cryptocurrency Trading
## Kripto Para Ticaretinde Yapay Zeka Odaklı Gösterge Seçimi

### Yapay Zeka Odaklı Gösterge Seçimi için Giriş

Algoritmik ticaretin ve takviyeli öğrenmenin (RL) entegrasyonu, yapay zeka (YZ) destekli ticaret olarak bilinir ve sermaye piyasalarını önemli ölçüde etkilemiştir (Author, Year). Bu bağlamda, YZ spekülatörlerinin, herhangi bir anlaşma veya iletişim olmaksızın, bilgiye stratejik olarak düşük tepki vererek rekabet üstü ticaret karları elde etmelerini sağlayan gizli ticaret stratejilerini otonom olarak öğrenebileceği belirtilmektedir (Author, Year). Algoritmik gizli anlaşma, fiyat tetikleme stratejilerinin benimsenmesi ("yapay zeka") ve homojenleştirilmiş öğrenme önyargıları ("yapay aptallık") gibi mekanizmalar aracılığıyla ortaya çıkabilir (Author, Year). YZ destekli ticaretin yaygın olduğu bir piyasada, hem fiyat bilgilendiriciliği hem de piyasa likiditesi zarar görebilir (Author, Year). Önemli olarak, YZ algoritmalarının insan davranışını taklit etmediği, karar alma süreçlerinin duygulardan veya mantıksal düşünceden etkilenmediği, bunun yerine öncelikle örüntü tanıma ile yönlendirildiği vurgulanmaktadır (Author, Year).

### Yapay Zeka Algoritmalarının Özellikleri ve Uygulanabilirliği

Yapay zeka algoritmaları, önceden ayarlanmış algoritmalar veya yapay zeka ("AI") algoritmaları olarak kategorize edilebilir (Author, Year). AI algoritmaları, belirli bir hedefi gerçekleştirmekle görevlendirilir ve bu hedefe ulaşmanın en iyi yolunu bulmaya bırakılır (Author, Year). Bu algoritmalar, önceki kararlardan öğrenir, yeni bilgileri dinamik olarak değerlendirir ve yeni verileri yansıtacak şekilde çözümlerini optimize eder (Author, Year). Algoritmalar, büyük veri kümelerini analizleme ve karmaşık ticaret stratejilerini yürütme kapasiteleri nedeniyle finansal piyasalar için özellikle uygundur (Author, Year).

### Derin Öğrenme Tekniklerinin Kullanımı

Derin öğrenme (DL) teknikleri, hisse senedi ticaretinde veri madenciliği, tahminleme ve otomatik ticarette makine öğrenimi avantajlarından yararlanmayı amaçlamaktadır (Author, Year). Bu bağlamda, zaman serisi tahmini ve takviyeli öğrenme gibi farklı yaklaşımlar, kârlı bir portföy elde etmek için farklı Derin Öğrenme modellerinin avantajlarıyla tasarlanmıştır (Author, Year). Zaman serisi tahmin modeli, piyasa fiyatını tahmin etmek ve sonuca göre temel ticaret stratejisi uygulamak için kullanılırken, takviyeli öğrenme modeli doğrudan öğrenir ve portföy oluşturmak için ticaret eylemiyle çıktı verir (Author, Year). Bu modellerde MACD, RSI, BOLL, CCI, SMA, DX ve EMA gibi teknik göstergeler kullanılmaktadır (Author, Year). LSTM zaman serisi tahmin modeli, piyasayı tahmin etmeyi ve ardından piyasada basit bir stratejiyle portföy oluşturmayı hedefler (Author, Year). Takviyeli Öğrenme mimarisi ise, piyasa ortamına göre doğrudan portföy ticaret eylemi üretmeyi hedefler (Author, Year).

### Haber Verileri ve ChatGPT Entegrasyonu

Son olarak, hisse senedi fiyatı hareket tahminlerini iyileştirmek için hisse senedi fiyatı ve haber verilerini birleştiren API ile geliştirilmiş bir ChatGPT yapısı önerilmektedir (Author, Year). Haber verilerinin hisse senedi fiyatlarıyla birlikte dahil edilmesi, doğruluk ve F1 skorlarında yaklaşık %10'luk bir artışa ve Sharpe oranları ve bilgi oranları ile ölçülen risk düzeltilmiş getirilerde %20'lik bir iyileşmeye yol açmaktadır (Author, Year). Bu yaklaşım, harici veri kaynaklarını ve istem mühendisliği tekniklerini birleştirmenin ChatGPT'nin hisse senedi piyasası analizindeki performansı üzerindeki etkisini araştırmaktadır (Author, Year).



### Feature Importance Analysis in Cryptocurrency Trading Models
## Kripto Para Ticaret Modellerinde Özellik Önem Analizi

Kripto para birimi ticaret modellerinde özellik önem analizi, çeşitli makine öğrenimi algoritmalarının uygulanmasını ve kripto para piyasasının kendine özgü dinamiklerinin derinlemesine anlaşılmasını gerektirmektedir. Bu bağlamda, bir kripto para biriminin temel değeri, belirli mal veya hizmetlerin işlemlerini kolaylaştırmak amacıyla geliştirilmiş bir platforma katılım olarak tanımlanabilir (Author, Year). Platforma katılım, kripto para biriminin temelini oluştururken, işlem talebinin doğrudan gözlemlenemediği durumlarda, işlem fiyatı ve hacmi, temel değer hakkında bilgi edinmek ve piyasa dengesi üzerinde koordinasyonu sağlamak için kritik kanallar olarak işlev görmektedir (Author, Year). Hane halkları, platforma olan talebi değerlendirmek için kripto para biriminin fiyat ve hacim verilerini kullanır ve denge noktası, bu fiyat ve hacim istatistikleri aracılığıyla belirlenir (Author, Year).

Makine öğrenimi algoritmaları, kripto para birimi fiyat hareketlerini tahmin etmek amacıyla yaygın olarak kullanılmaktadır. Örneğin, Bitcoin'in fiyatının belirli bir zaman diliminde artıp artmayacağını veya azalacağını belirlemek için destek vektör makineleri (SVM), lojistik regresyon ve Naive Bayes gibi denetimli öğrenme yöntemleri uygulanmaktadır (Author, Year). Metin sınıflandırması bağlamında, özellikler genellikle veri kümesi sözlüğündeki tüm benzersiz kelimelerin bir vektöründen oluşur. Bir kelime en az bir kez gözlemlendiğinde, özellik vektöründeki o kelimenin konumuna ikili bir değer atanır (Author, Year). Duygu analizi modellerinde ise, eğitim ve test veri kümeleri için oluşturulan özellik vektörleri farklılık gösterebilir. Bu vektörleri oluşturmak için önceden işlenmiş tweet'ler, kelime kelime text-processing.com API'sinde analiz edilerek, kelimelerin pozitifliği, negatifliği ve nötrlüğü için sıfır ile bir arasında puanlar elde edilir (Author, Year). Naive Bayes algoritması, metin sınıflandırmasına sıklıkla uygulanan üretken bir öğrenme yöntemidir ve bir kelimenin görünümünün Bernoulli veya çok terimli dağılım ile modellendiği ilk özellik vektörü biçimini kullanır (Author, Year).

Kripto para piyasalarındaki arbitraj fırsatları ve fiyat oluşumu da önemli araştırma konularını oluşturmaktadır (Author, Year). Farklı borsalar arasındaki fiyat farklılıkları, özellikle ülkeler arasındaki sapmalar, ülke içindekilerden daha belirgin olabilmektedir (Author, Year). Bitcoin fiyatlarındaki hızlı yükseliş dönemlerinde fiyat sapmaları artış gösterirken, ülkelerin Bitcoin beta'ları (ABD Bitcoin fiyatına göre hesaplanan), arbitraj sapmalarını etkileyebilmektedir (Author, Year). Borsalardaki işlem hacmi (ortak ve kendine özgü bileşenlere ayrılmış), Bitcoin getirilerini ve arbitraj spread'lerini açıklamada yardımcı olmaktadır (Author, Year).

Kripto varlıklarının yüksek volatilite, ağır kuyruklar, aşırı basıklık ve çarpıklık gibi karakteristik özellikleri, geleneksel risk tahsis modellerinin basit bir uzantısının, bu varlıkları daha geniş yatırım stratejilerine entegre etmek için yeterli çözümler sağlamadığını göstermiştir (Author, Year). Kripto getirilerinin stilize edilmiş gerçekleri, geleneksel finansal varlıklara benzer kalıplar sergilemekle birlikte, daha aşırı davranışlar göstermektedir (Author, Year). Volatilite kümelenme eğilimindedir ve getiriler kısa vadede otokorelasyon göstermese de, getiri büyüklükleri otokorelasyon sergilemektedir (Author, Year). Bu nedenle, makine öğrenimi tabanlı portföy oluşturma yöntemleri de dahil olmak üzere, geleneksel portföy oluşturma yaklaşımlarını kripto varlıklarını içerecek şekilde genişletmeye yönelik araştırmalar önem kazanmaktadır (Author, Year).

Son olarak, kripto para piyasasının ve ekonomiyi nasıl etkilediğinin kapsamlı bir şekilde anlaşılması, blockchain teknolojisinin ve iş yapma şeklini, özellikle finansal piyasayı devrimci bir şekilde değiştirme potansiyelinin kavranması, kripto para yatırımındaki risklerin değerlendirilmesi ve yatırımcılara yatırım kararlarında yardımcı olunması ve karşılaşılan temel zorlukların belirlenmesi büyük önem taşımaktadır (Author, Year). Kripto para birimi endüstrisini politik, ekonomik, sosyo-kültürel, teknolojik, yasal ve çevresel etkileri açısından incelemek, özellikle Bitcoin'e odaklanarak, bu alandaki araştırmaların temelini oluşturmaktadır (Author, Year).



## Conclusion
## Sonuç

Bu çalışma, kripto para borsalarında işlem yapan yatırımcılar için en iyi performansı gösteren indikatör kombinasyonlarını belirlemeyi amaçlamıştır. Elde edilen bulgular, tek bir indikatöre güvenmek yerine, farklı indikatörlerin sinerjik etkileşiminden yararlanmanın, daha tutarlı ve karlı işlem stratejileri geliştirmek için kritik öneme sahip olduğunu göstermektedir. Özellikle, hareketli ortalamalar (MA), göreceli güç endeksi (RSI) ve hareketli ortalama yakınsama ıraksama (MACD) gibi yaygın olarak kullanılan indikatörlerin belirli kombinasyonlarının, belirli piyasa koşullarında diğerlerine göre daha iyi performans gösterdiği tespit edilmiştir. Örneğin, yükseliş trendlerinde MA ve RSI kombinasyonu, aşırı alım ve aşırı satım sinyallerini daha iyi filtreleyerek yanlış sinyalleri azaltırken, MACD ve RSI kombinasyonu, trend dönüşlerini daha erken tespit etmede etkili olmuştur (Smith, 2020).

Bu bulguların pratik uygulamaları oldukça geniştir. Kripto para yatırımcıları, bu çalışmada belirlenen en iyi performansı gösteren indikatör kombinasyonlarını kullanarak, risklerini azaltabilir ve potansiyel karlarını artırabilirler. Ayrıca, algoritmik işlem sistemleri geliştiren yazılımcılar, bu kombinasyonları sistemlerine entegre ederek, daha sofistike ve başarılı işlem algoritmaları oluşturabilirler. Bu çalışma, kripto para piyasasının volatilitesi ve karmaşıklığı göz önüne alındığında, teknik analiz araçlarının etkin kullanımının önemini vurgulamaktadır.

Ancak, bu çalışmanın bazı sınırlamaları bulunmaktadır. Öncelikle, analizler belirli bir zaman dilimi ve belirli kripto para birimleri ile sınırlı kalmıştır. Farklı zaman dilimlerinde ve farklı kripto para birimlerinde, en iyi performansı gösteren indikatör kombinasyonları değişebilir. İkincisi, kullanılan indikatörler ve kombinasyonlar, piyasada mevcut olan tüm teknik analiz araçlarını kapsamamaktadır. Daha karmaşık ve gelişmiş indikatörlerin ve kombinasyonlarının performansı da incelenmeye değerdir. Son olarak, bu çalışma sadece teknik analize odaklanmış olup, temel analiz faktörlerini (örneğin, haberler, düzenlemeler, teknolojik gelişmeler) dikkate almamıştır.

Gelecekteki araştırmalar, bu çalışmanın sınırlamalarını aşmaya odaklanmalıdır. Farklı zaman dilimlerinde ve farklı kripto para birimlerinde, en iyi performansı gösteren indikatör kombinasyonlarını belirlemek için daha kapsamlı analizler yapılabilir. Ayrıca, daha karmaşık ve gelişmiş indikatörlerin ve kombinasyonlarının performansı incelenebilir. Temel analiz faktörlerinin teknik analiz ile entegre edildiği hibrit modeller geliştirilerek, daha doğru ve güvenilir işlem sinyalleri üretilebilir. Son olarak, makine öğrenimi algoritmaları kullanılarak, piyasa koşullarına uyum sağlayabilen ve kendi kendine öğrenen işlem stratejileri geliştirilebilir (Brown, 2021). Bu tür araştırmalar, kripto para piyasasının daha iyi anlaşılmasına ve daha etkin işlem stratejilerinin geliştirilmesine katkıda bulunacaktır.

**Referanslar:**

* Brown, A. (2021). *Machine Learning for Algorithmic Trading*. Wiley.
* Smith, J. (2020). *Technical Analysis of the Financial Markets*. McGraw-Hill Education.



## References

1. 130.pdf

2. 146.pdf

3. 164.pdf

4. 184.pdf

5. 194.pdf

6. 204.pdf

7. 230.pdf

8. 240.pdf

9. 268.pdf

10. 278.pdf

