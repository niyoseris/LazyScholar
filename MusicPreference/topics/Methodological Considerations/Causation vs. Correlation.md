# Causation vs. Correlation

### Methodological Considerations

#### Causation vs. Correlation

A critical methodological consideration in research is the distinction between correlation and causation. Correlation indicates the degree to which two variables are related, either linearly or non-linearly, implying a pattern or relationship between their values (Author, Year). This relationship can be causal or non-causal (Author, Year). Causation, on the other hand, signifies that one event or variable directly influences another (Author, Year). It is defined counterfactually, such as "smoking causes cancer relative to what would have happened if not smoking" (Author, Year). While correlations can be informative and point towards possible explanations, they do not prove or imply causation (Author, Year). Statistical tests, such as the Pearson r correlation coefficient for linear relationships, can quantify the strength and direction of a correlation (Author, Year). However, it is crucial to remember that "correlation does NOT imply causation" (Author, Year).

Establishing causation requires a carefully designed experiment with different treatments for similar groups (Author, Year). Even when a correlation exists, concluding that one variable causes a change in another is problematic (Author, Year). The observed relationship might be coincidental, or a third, unmeasured variable might be influencing both variables (Author, Year). These spurious correlations arise when a causal link doesn't exist between two measured variables, but both are related to a third variable (Author, Year). Furthermore, determining the direction of causation can be challenging; a correlation between A and B does not necessarily mean A causes B; it could be that B causes A (Author, Year). Selection bias can also lead to deceptive correlations (Author, Year).

To illustrate, examples such as co-ed dorms and binge drinking, police force size and crime rates, family dinners and grades, education and earnings, firemen and fire damage, and limousines and salaries are often cited as instances where correlation does not equal causation (Author, Year). Approaching correlational evidence with skepticism is therefore essential (Author, Year). The only way to ensure that selection bias is not operating is to conduct a true experiment in which the variables are manipulated (Author, Year).

The concept of causality can be further understood through the lens of potential outcomes. If we define treatment (T) as 1 (received) or 0 (placebo), and potential outcomes as Y0 (no treatment) and Y1 (treated), the causal effect for individual i is Y1,i - Y0,i (Author, Year). The fundamental challenge is that we never observe both Y1,i and Y0,i for the same individual (Author, Year). The average causal effect is E(Y1,i - Y0,i) = E(Y1,i) - E(Y0,i) (Author, Year). The difference in means, E(Y|Ti=1) - E(Y|Ti=0), is related to the correlation between Y and T, but is not necessarily equal to the average causal effect (Author, Year). However, in experiments, if (Y1,i, Y0,i) is independent of Ti, then E(Y|Ti=1) - E(Y|Ti=0) = E(Y1,i - Y0,i) (Author, Year). Similarly, under conditional independence, if (Y1,i, Y0,i) is independent of Ti given Xi, then E(Y|Ti=1, Xi=x) - E(Y|Ti=0, Xi=x) = E(Y1,i - Y0,i | Xi=x) (Author, Year).

In the context of machine learning (ML) models, an accurate model does not have to have causal output to be useful in a properly constructed context (Author, Year). Strategies to gain insight into causal vs. correlative features learned by a model include multi-disciplinary teams reviewing false positive and false negative cases, and testing the model on external datasets (Author, Year). Given that ML models may lack common sense, the involvement of domain experts is crucial (Author, Year). While explainability is often desired, clinicians and regulators should not always insist on it (Author, Year). Black box models, characterized by low model interpretability, are especially important to evaluate with empirical pilot testing, preferably on prospective data, external data and potentially in a trial setting (Author, Year). Both black box and transparent model performance should be evaluated against existing standards of care on real-world data to evaluate effectiveness in their specific patient population (Author, Year).


## References

1. SOURCE: Correlation%20and%20Causation.pdf
2. SOURCE: Correlation%20and%20Causation.pdf
3. SOURCE: Stanovich%20Chapter%205%20Presentation%20finished.pdf
4. SOURCE: Stanovich%20Chapter%205%20Presentation%20finished.pdf
5. SOURCE: Causality2_310_2015.pdf
6. SOURCE: Causality2_310_2015.pdf
7. SOURCE: Correlation-Causation-Teacher-Guide-2.pdf
8. SOURCE: Correlation-Causation-Teacher-Guide-2.pdf
9. SOURCE: BIODS388_Lecture_7.pdf
10. SOURCE: BIODS388_Lecture_7.pdf
