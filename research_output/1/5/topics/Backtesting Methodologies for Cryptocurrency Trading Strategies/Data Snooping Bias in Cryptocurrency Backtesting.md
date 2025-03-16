# Data Snooping Bias in Cryptocurrency Backtesting

### Data Snooping Bias in Cryptocurrency Backtesting

Data snooping, also referred to as data mining, arises when a specific dataset is repeatedly utilized for inference or model selection purposes (White, 2000). This repeated use of data introduces the risk that seemingly satisfactory results are attributable to chance rather than the inherent merit of the method employed (White, 2000). While empirical researchers widely acknowledge data snooping as a perilous practice to avoid, it is, in reality, endemic (White, 2000). A core challenge lies in the scarcity of readily applicable methods to assess the potential dangers of data snooping in a given context (White, 2000). In the context of financial time series analysis, this issue is practically unavoidable due to the limited availability of historical data measuring the specific phenomenon of interest (White, 2000).

The low signal-to-noise ratio inherent in financial data, coupled with survival bias in historical data and the overfitting of models during backtesting, complicates the creation of high-quality market environments and benchmarks for financial reinforcement learning (FinRL) (FinRL-Meta kütüphanesi). This, in turn, diminishes the performance of DRL strategies in real-world markets (FinRL-Meta kütüphanesi). Furthermore, manipulative practices such as wash trading, where investors simultaneously buy and sell the same assets to create artificial market activity, can distort prices, volume, and volatility, eroding investor confidence (Çalışma). Studies indicate that wash trading is prevalent on unregulated exchanges, inflating reported volumes by over 70% (Çalışma). This manipulation can improve an exchange's ranking, influence short-term price distributions, and is more common on newly established exchanges (Çalışma).

To address the challenges posed by data snooping, White (2000) introduced the Reality Check for Data Snooping, a significant contribution to comparing a benchmark model against multiple competitors. This approach controls the overall error rate when comparing numerous models, acknowledging that the probability of selecting an alternative model by chance increases with the number of competitors (White, 2000). White's Reality Check offers a novel method for controlling the probability of rejecting a true null hypothesis (White, 2000). While White's Reality Check addresses scenarios where parameter estimation error is negligible, Corradi and Swanson (2006a, 2007a) developed bootstrap procedures that account for the contribution of parameter estimation errors in rolling or recursive forecasting schemes.


## References

1. 165.pdf
2. 166.pdf
3. 167.pdf
4. 168.pdf
5. 171.pdf
6. 172.pdf
7. 173.pdf
8. 174.pdf
