# Regression Analysis for Vaccine Exposure and Mortality

### Aşıya Maruz Kalma ve Mortalite için Regresyon Analizi

COVID-19 aşılarının mortalite üzerindeki etkilerini değerlendirmek ve aşılanan gruplar arasındaki seçim yanlılığını (selection bias) incelemek amacıyla regresyon analizleri sıklıkla kullanılmaktadır. Bir çalışmada, Milwaukee County, Wisconsin'deki yetişkinlerin aşı ve ölüm kayıtları kullanılarak Pfizer ve Moderna COVID-19 aşılarının mortalite üzerindeki etkileri incelenmiştir. Araştırmacılar, COVID-19'a bağlı ölümleri, COVID-19 dışı doğal ölümlere oranlayarak elde edilen COVID-19 Aşırı Mortalite Yüzdesi (CEMP) ölçüsünü, seçim etkilerini kontrol etmek için bir vekil olarak kullanmışlardır. Bu çalışma, aşıların göreli mortalite risklerini (RMR) değerlendirirken, yaş, aşı türü, doz sayısı ve zaman dilimi gibi faktörleri dikkate alarak regresyon analizleri uygulamıştır. Bulgular, 60 yaş üstü kişilerde iki doz Pfizer aşısı alanların RMR'sinin, Moderna aşısı alanlara göre daha yüksek olduğunu göstermiştir. Zamanla her iki aşının etkinliğinin azaldığı, özellikle 60 yaş üstü kişilerde gözlemlenirken, güçlendirici doz alanlarda Pfizer-Moderna arasındaki farkın azaldığı belirtilmiştir.

Lojistik regresyon, ikili bir olayın (örneğin, hastalık/sağlıklı) riskini tahmin etmek için kullanılan bir yöntemdir. Bu bağlamda, aşılamanın ölüm üzerindeki etkisini incelemek için lojistik regresyon kullanılmıştır. Lojistik regresyon, risk oranlarını her zaman geçerli bir şekilde tahmin etmeyebilir, ancak odds oranlarını geçerli bir şekilde tahmin eder. Çalışma tasarımının önemi vurgulanarak, takip çalışmalarında risk hesaplanabilirken, vaka-kontrol çalışmalarında risk oranının hesaplanamayacağı belirtilmiştir. Ancak, odds oranı her iki durumda da hesaplanabilir. Yordayıcı nicel ise (doz) veya birden fazla yordayıcı varsa, lojistik regresyon kullanımı uygundur. Lojistik regresyonda, logit dönüşümü, olasılıklar ölçeğindeki 0 ile 1 arasındaki bir sayıyı alır ve doğrusal bir yordayıcının ölçeği olan pozitif veya negatif herhangi bir şey olabilen bir sayı üretir.

Zamanla değişen tedavilerin (örneğin, aşı) etkisini değerlendirmek için marjinal yapısal modeller (MSM'ler) kullanılabilir. MSM'ler, zamanla değişen ve önceki tedavilerden etkilenen karıştırıcı faktörlerin varlığında, ters olasılıklı ağırlıklandırma (IPTW) ile tahmin edilen parametrelere sahip yeni bir nedensel model sınıfıdır ve karıştırıcı faktörlere uygun şekilde ayarlama sağlar. Standart Cox orantılı tehlikeler modeli, zamanla değişen karıştırıcı faktörler olduğunda yanlı sonuçlar verebilir.

Aşı güvenliğini değerlendirmek için kullanılan istatistiksel yöntemlere değinen çalışmalar da mevcuttur. Örneğin, Huang ve diğerleri (2021), Aşı Yan Etki Raporlama Sistemi (Vaccine Adverse Event Reporting System) kullanılarak, advers olayların zamansal değişimini inceleyerek aşı güvenliğini izlemeyi amaçlamışlardır (Huang et al., 2021). Ayrıca, hayatta kalım analizleri, kantil regresyonu ve uzunlamasına veri analizi gibi istatistiksel yöntemler de aşı güvenliği araştırmalarında kullanılmaktadır.

**Referans:**

Huang, J., Cai, Y., Du, J., Li, R., Ellenberg, S., Hennessy, S., Tao, C., Chen, Y. (2021). Monitoring vaccine safety by studying temporal variation of adverse events using Vaccine Adverse Event Reporting System.


## References

1. 165.pdf
2. 166.pdf
3. 167.pdf
4. 168.pdf
5. 169.pdf
6. 170.pdf
7. 171.pdf
8. 172.pdf
9. 173.pdf
10. 174.pdf
