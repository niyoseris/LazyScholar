# Overfitting Prevention in Cryptocurrency Backtesting

### Kripto Para Birimi Geriye Dönük Testlerinde Aşırı Uyumun Önlenmesi

Aşırı uyum (overfitting), bir modelin eğitim verilerine aşırı derecede iyi uyum sağlaması, ancak yeni verilerde (test verileri) daha kötü performans göstermesi durumudur (Author, Year). Bu durum, modelin eğitim verilerindeki gürültüyü veya rastlantısal varyasyonları öğrenmesi ve genelleme yeteneğini azaltmasıyla ortaya çıkar (Author, Year). Kripto para birimi ticaret stratejilerinin geriye dönük testlerinde aşırı uyumu önlemek için çeşitli metodolojiler mevcuttur.

**Aşırı Uyumun Önlenmesi Yaklaşımları**

Aşırı öğrenmeyi önlemek için çeşitli yaklaşımlar mevcuttur (Author, Year):

*   **Ceza Yöntemleri:** Bu yöntemler, modelin karmaşıklığına bir ceza ekleyerek aşırı uyumu engellemeyi amaçlar. Amaç, eğitim hatasını (εtrain) ve bir ceza terimini birleştirerek test hatasını (εtest) tahmin etmektir. Maksimum A Posteriori (MAP) gibi yöntemler, daha karmaşık hipotezlere daha düşük önsel olasılık atayarak cezalandırır (Author, Year). Amaç fonksiyonu (J) şu şekilde tanımlanır: J(w) = εtrain(w) + ceza(w) (Author, Year).

*   **Doğrulama ve Çapraz Doğrulama Yöntemleri:** Bu yöntemler, verileri eğitim ve doğrulama kümelerine ayırarak aşırı uyumun ne zaman meydana geldiğini deneysel olarak belirlemeyi amaçlar (Author, Year). K-katlı çapraz doğrulama, verileri k alt kümeye ayırır ve her birini doğrulama kümesi olarak kullanarak modeli k kez eğitir (Author, Year). Holdout yöntemi, eğitim kümesinin bir alt kümesini (Seval) kullanarak hipotez uzayını ve karmaşıklığını belirler (Author, Year). Çapraz doğrulama, holdout yöntemini birden çok kez tekrarlar ve sonuçları ortalar (Author, Year). Test seti yöntemi, verilerin bir kısmını test seti olarak ayırarak modelin gelecekteki performansı hakkında bir fikir edinmeyi amaçlar (Author, Year). Ancak, bu yöntem veri kaybına neden olabilir ve küçük veri setlerinde güvenilir sonuçlar vermeyebilir (Author, Year). Leave-one-out çapraz doğrulama (LOOCV) yöntemi, her bir veri noktasını ayrı ayrı test seti olarak kullanarak daha az veri kaybı sağlar, ancak hesaplama maliyeti yüksektir (Author, Year). k-fold çapraz doğrulama, veri setini k parçaya ayırarak her bir parçayı test seti olarak kullanır ve daha dengeli bir yaklaşım sunar (Author, Year).

*   **Topluluk Yöntemleri:** Bu yöntemler, birden fazla modelin tahminlerini birleştirerek daha iyi genelleme performansı elde etmeyi amaçlar (Author, Year). Tam Bayes yöntemleri, birçok hipotezi oylar. Torbalama (Bagging) ve Rastgele Ormanlar (Random Forests) diğer topluluk yöntemleridir (Author, Year). Torbalama, aşırı uyumun yüksek varyanstan kaynaklandığı durumlarda yardımcı olabilir (Author, Year). Ensemble yöntemleri, birden fazla hipotezin birleşimini kullanır (Author, Year).

**Kısıtlamalar ve Dikkat Edilmesi Gerekenler**

Makine öğrenimi, büyük veri miktarlarında aşırı uyumu önlemek için tasarlanmıştır, ancak yatırım finansmanında veri sınırlıdır ve çapraz doğrulama, boyutluluk lanetini hafifletmez (Author, Year). K-katlı çapraz doğrulama ile 10 farklı hiperparametre ayarlamak, 50 yıllık verilerle getirileri tahmin etmeye çalışıyorsanız kötü bir fikirdir (Author, Year). Hisse senedi verileri sınırlıdır ve çoğu makine öğrenimi uygulaması için çok küçüktür (Author, Year). Yanlış bir stratejinin çapraz doğrulanmış örnekte işe yaraması mümkündür; bu durumda, çapraz doğrulama rastgele değildir; sonuç olarak, tek bir tarihsel yol bulunabilir (Author, Year). Sınırlı veri nedeniyle güçlü aşırı uyum belirtileri gözlemlenmektedir (Author, Year). Bu nedenle, veri kümesini genişletmenin ve aşırı uyumu önlemenin yollarını araştırmak önemlidir (Author, Year).


## References

1. 155.pdf
2. 156.pdf
3. 157.pdf
4. 158.pdf
5. 159.pdf
6. 160.pdf
7. 161.pdf
8. 162.pdf
9. 163.pdf
10. 164.pdf
