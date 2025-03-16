# Walk-Forward Optimization in Cryptocurrency Backtesting

### Geriye Dönük Testte İleriye Dönük Optimizasyon: Mevcut Literatürdeki Boşluklar

Kripto para birimi ticaret stratejileri için geriye dönük test metodolojileri, strateji performansını değerlendirmek için hayati öneme sahiptir. Ancak, mevcut literatürde ileriye dönük optimizasyon (walk-forward optimization) gibi belirli geriye dönük test tekniklerine odaklanan çalışmalar sınırlıdır. Birçok çalışma, portföy optimizasyonu, risk yönetimi ve Black-Litterman modeli gibi farklı konulara odaklanmakta ve ileriye dönük optimizasyon hakkında doğrudan bilgi sağlamamaktadır (Author, Year).

Geriye dönük testin kendisi, doğru uygulandığında değerli bir doğrulama aracı olarak kabul edilmektedir (Author, Year). Ancak, aşırı uyum (overfitting) ve seçilim yanlılığı gibi potansiyel tuzaklara dikkat çekilmektedir. Çok sayıda geriye dönük testin yapılması ve en iyi performans gösteren testin tek bir deneme gibi sunulması, yanıltıcı sonuçlara yol açabilir ve finans alanındaki birçok yanlış keşfin nedeni olabilir (Author, Year). Ayrıca, ileriye dönük test ile yüksek Sharpe oranları elde etmenin nispeten kolay olduğu, ancak akademik çalışmaların bu süreçte yapılan deneme sayısını genellikle belirtmediği vurgulanmaktadır (Author, Year).

Bollerslev ve ark. (2016), tahmin değerlendirmesi için hareketli pencereler (rolling windows) kullanmaktadır. Bu yaklaşım, bir modelin belirli bir zaman aralığında (N uzunluğunda bir pencere) tahmin edilmesini ve ardından pencerenin bir adım ileri kaydırılarak tahmin işleminin tekrarlanmasını içerir. Her adımda, modelin parametreleri yeniden tahmin edilir ve bir sonraki değer için bir tahmin oluşturulur. Tahmin hatası hesaplanır ve ortalama karesel tahmin hatası (MSE), modelin tahmin doğruluğunu ölçmek için kullanılır. Farklı modelleri karşılaştırmak için, her model için MSE hesaplanır ve daha düşük MSE'ye sahip model, örnek dışı tahminlerde daha iyi performans gösterir. Karşılaştırmaların adil olması için, her modelin aynı zaman dilimlerinde tahmin edilmesi gerekir (Bollerslev et al., 2016). Bu yöntem, ileriye dönük optimizasyonun temel prensiplerini yansıtsa da, kripto para birimi ticaret stratejileri bağlamında doğrudan uygulanabilirliği ve etkinliği daha fazla araştırma gerektirmektedir.

Sonuç olarak, kripto para birimi ticaret stratejileri için ileriye dönük optimizasyonun kullanımı ve etkinliği hakkında daha fazla araştırmaya ihtiyaç vardır. Mevcut literatür, geriye dönük testin potansiyel tuzaklarına ve sağlam teoriler geliştirmenin önemine dikkat çekmektedir (Author, Year). Bu nedenle, bu çalışma, ileriye dönük optimizasyonun kripto para birimi ticaret stratejileri üzerindeki etkisini daha derinlemesine incelemeyi amaçlamaktadır.


## References

1. 147.pdf
2. 148.pdf
3. 149.pdf
4. 150.pdf
5. 151.pdf
6. 152.pdf
7. 153.pdf
8. 154.pdf
