# Time-Series Analysis of Vaccination and Mortality Trends

### Aşı ve Ölüm Oranları Arasındaki İlişkilerin Analizinde Zaman Serisi Yöntemleri: Aşılama ve Ölüm Eğilimlerinin Zaman Serisi Analizi

Zaman serisi analizi, zaman içinde sıralı olarak elde edilen gözlemlerin incelenmesinde kullanılan güçlü bir araçtır (Author, Year). Örneğin, günlük ölüm sayıları bir zaman serisi olarak değerlendirilebilir. Bu tür verilerin analizinde, stokastik bir süreç şeklinde istatistiksel bir model oluşturmak faydalıdır (Author, Year). Bu bağlamda, durağanlık kavramı, zaman serisinin istatistiksel özelliklerini tanımlamada önemli bir rol oynar. Geniş anlamda, bir zaman serisi, sistematik bir eğilim, sistematik bir varyans değişikliği ve belirgin periyodik varyasyonlar veya mevsimsellik içermiyorsa durağan olarak kabul edilir (Author, Year). İki zaman serisi arasındaki ilişkiyi belirlemek için çapraz korelasyon fonksiyonu kullanılabilirken, spektral analiz, zaman serisinin özelliklerini frekans alanında incelemek için uygundur (Author, Year). Ayrıca, periyodogram, sinyaldeki periyodiklikleri (deterministik olanları) tespit etmede yararlıdır (Author, Year). Zamanla değişen spektral yoğunluğu tahmin etmek için dinamik periyodogram kullanılabilir (Author, Year).

Zaman serisi verileri, tek bir birimin birçok zaman periyodu boyunca gözlemlenmesiyle elde edilir (Author, Year). Ekonometricinin temel görevi, hem çıkarım hem de tahmin amacıyla stokastik süreci doğru bir şekilde modellemektir (Author, Year). Birçok zaman serisi süreci, gecikmeli (geçmiş) değerler üzerine eklenen bozulmalarla regresyonlar veya inovasyonların geçmişinin toplamları olarak görülebilir (Author, Year). Örneğin,  𝑦𝑡=𝜌1𝑦𝑡−1+𝑒𝑡 modeli, otoregresif süreç (AR(1)) için bir örnektir (Author, Year). Bir serinin regresyon analizinde kullanılabilmesi için, beklenen bir değere, varyansa ve otokovaryansa sahip olması gerekir (Author, Year). Durağanlık özelliği, E(𝑦𝑡)'nin t'den bağımsız olmasını, Var(𝑦𝑡)'nin t'den bağımsız sonlu bir pozitif sabit olmasını ve Cov(𝑦𝑡,𝑦𝑡−𝑠)'nin t veya s'den değil, t−s'nin sonlu bir fonksiyonu olmasını gerektirir (Author, Year). Zayıf bağımlılık varsayımı başarısız olsa bile, yani 𝜌1=1 olsa bile, otoregresif bir süreç, durağan olmayan, güçlü bir şekilde bağımlı süreci durağan hale getiren (1. fark) dönüştürülmüş bir OLS modeli kullanılarak analiz edilebilir (Author, Year).

Bağımlı değişkenin açıklayıcı değişkenin eşzamanlı ve geçmiş değerlerinin bir fonksiyonu olduğu modellere "sonlu dağıtılmış gecikme" (FDL) modelleri denir (Author, Year). Bir FDL modelinin derecesi, y'yi tahmin etmek için kaç gecikmenin alakalı olduğunu gösterir (Author, Year).

Ekolojik çalışmalar, gözlem biriminin bireyler değil, bir grup olduğu çalışmalardır (Author, Year). Zaman serisi ekolojik çalışmaları, aynı toplulukta zaman içinde toplu maruziyetler ve sonuçlardaki değişimleri karşılaştırır (Author, Year). Bu tür çalışmalarda, maruziyetin sonuçtan önce geldiğinden emin olunamayabilir (Author, Year). Topluluklara göçler de ekolojik sonuçların yorumlanmasını etkileyebilir (Author, Year). Kısa vadeli maruziyet değişikliklerinin (örneğin, sıcaklığın mortalite üzerindeki etkisi) etkisini incelemek için de faydalıdır (Author, Year).

Zaman serisi analizinin temel amaçları arasında veri kümesinin özlü bir şekilde tanımlanması, yorumlanması, tahminleme, kontrol, hipotez testi ve simülasyon yer alır (Author, Year). Zaman serisi modelleri, rassal değişkenlerin {Xt} dizisinin ortak dağılımını belirtir (Author, Year). Zaman serisi modellemesinde, öncelikle zaman serisi çizilir, trendler, mevsimsel bileşenler ve aykırı değerler aranır (Author, Year). Daha sonra, artıkların durağan olması için veri dönüştürülür (trend ve mevsimselliğin çıkarılması, fark alma, doğrusal olmayan dönüşümler) (Author, Year). Son olarak, artıklara model uydurulur (Author, Year). Fark alma (differencing) işlemi, trend ve mevsimselliği gidermek için kullanılır (Author, Year). Klasik ayrıştırma, Xt=Tt+St+Yt (Trend, Mevsimsellik, Geri Kalan) şeklinde ifade edilebilir (Author, Year). Mevsimsel varyasyon için lag-s fark operatörü: ∇sXt=Xt−Xt−s= (1−Bs)Xt (Author, Year).


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
