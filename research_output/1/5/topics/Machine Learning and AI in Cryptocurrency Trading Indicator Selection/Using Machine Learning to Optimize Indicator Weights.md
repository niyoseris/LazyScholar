# Using Machine Learning to Optimize Indicator Weights

### Makine Öğrenimi ile Gösterge Ağırlıklarını Optimize Etme

Kripto para birimi ticaretinde kullanılan teknik göstergelerin etkinliği, genellikle bu göstergelere atanan ağırlıklara bağlıdır. Makine öğrenimi, bu ağırlıkları optimize etmek için güçlü bir araç sunmaktadır. Bu bağlamda, makine öğrenimi hedefleri, bir modelin tahmin oranları üzerinde "oran kısıtlamaları" olarak ifade edilebilir (Author, Year). Bu durum, eğitim sürecini kısıtlı bir optimizasyon problemine dönüştürür. Basit bir örnek olarak, bir ikili sınıflandırıcının örneklerin en az %80'inde pozitif tahminler yapması istenebilir (Author, Year).

Kısıtlamalarla eğitim, çeşitli zorlukları beraberinde getirir. İlk olarak, sinir ağları gibi doğrusal olmayan fonksiyon sınıfları için, amaç ve kısıtlama fonksiyonları, dışbükey kayıp fonksiyonları kullanıldığında bile dışbükey olmayacaktır (Author, Year). İkinci olarak, oran kısıtlamaları, pozitif ve negatif sınıflandırma oranlarının doğrusal kombinasyonlarıdır ve bu nedenle gösterge fonksiyonlarından (0-1 kayıpları) oluşurlar. Bu durum, neredeyse her yerde sıfır gradyanlara yol açar, bu da optimizasyonu zorlaştırır (Author, Year).

Kısıtlı optimizasyon problemlerine Lagrange çarpanları yaklaşımının, dışbükey olmayan (non-convex) problemler için başarısız olabileceği belirtilmektedir (Author, Year). Ayrıca, kısıtlamalar türevlenebilir değilse, Lagrange fonksiyonunu gradyan tabanlı yöntemlerle optimize etmek mümkün değildir (Author, Year). Bu sorunları aşmak için, literatürde yeni "proxy-Lagrangian" formülasyonları önerilmektedir (Author, Year). Bu yaklaşımlar, bir optimizasyon oracle'ına erişim varsayılarak, kısıtlı optimizasyon problemine yaklaşık olarak optimal ve uygulanabilir bir çözüm olan yarı kaba ilişkili bir dengeyi çözen iki oyunculu sıfır toplamlı olmayan bir oyun oynayarak stokastik bir sınıflandırıcı üretmeyi amaçlar (Author, Year).

Alternatif bir yaklaşım, veri noktaları arasındaki mesafeyi tanımlayan bir mesafe fonksiyonu kullanarak verilerin sınıflandırılmasını içerir (Author, Year). Bu mesafe fonksiyonları genellikle ağırlıklar veya maliyetler kullanılarak tanımlanır ve bu ağırlıkların anlamlı bir şekilde ayarlanması önemlidir (Author, Year). Bu bağlamda, mevcut çalışmalar, bu ağırlıkları veri kullanarak öğrenen bir çerçeve sunmaktadır (Author, Year). Çerçevenin çalışma zamanını iyileştirmek için paralelleştirme teknikleri uygulanmış ve ağırlıkların nasıl optimize edileceğine dair sonuçlar sunulmuştur (Author, Year). Bu çerçeve, iki aşamada çalışır: İlk aşamada, bir mesafe matrisi hesaplanır; burada (i,j) girdisi, xi ve xj veri noktaları arasındaki mesafedir. İkinci aşamada, bu mesafe matrisi ağırlık kümesini optimize etmek için kullanılır (Author, Year). Mesafe matrisinin hesaplanmasının çalışma zamanını hızlandırmak için paralelleştirme tanıtılmıştır ve ağırlıkları optimize etmenin bir yolu hakkında sonuçlar sunulmaktadır (Author, Year).


## References

1. 241.pdf
2. 242.pdf
3. 245.pdf
4. 246.pdf
5. 247.pdf
6. 248.pdf
7. 249.pdf
8. 250.pdf
