# Options + Background
## What is an option?
An option is a contract between a buyer and a seller. The buyer pays some **option premium** for the right to buy (**call**) or sell (**put**) a stock at a set price (**strike price**) before the **expiration date**. In return, the seller agrees to sell or buy the stock at that set price *iff* if the buyer decides to exercise their right. 

It allows the buyer to control more stock with less initial investment. If it is a call option and strike price < market price at expiration date, or if it is a put option and strike price > market price at expiration date, buyer makes money. Otherwise, buyer simply has lost the option premium. Assuming the expected value of money made > option premium, this is worth it for a buyer. 

For the seller, it generates income from premiums from a portfolio even in a stagnant/flat market where stocks are not increasing in price. 

Unlike buying stocks, which is only worth it when they're going to increase in price, options allow traders to benefit from falling prices using put options. It provides a lot of new and unique ways to bet on the market. 

## Calculating market price

The **market price** of a stock is the price on which both buyers and sellers can settle, determined by supply and demand. 

One way to calculate market price is **put-call parity aggregation**. As the name suggests, this compiles puts and calls which are of the most similar value. The market price can be the midpoint between the best bid (the highest someone will buy for) and the best ask (the lowest someone will sell for); it can also be weighted by the amount of puts/calls at those values. 

**Put-call parity** is a method which says that
$C-P=S_0-Ke^{-rT}$: that is to say if you hold a call and a put each with expiry $T$ and strike price $K$, your portfolio will be worth $S_0=Ke^{-rT}$. $S_0$ is log return (see below). To explain this consider that if $S_T>K$ you will call and earn $S_T-K$; if $S_T<K$ you will put and earn $S_T-K$... eh i don't really understand this and it doesn't matter much. 

Finally, the simplest method is the **last traded price**. This can be inaccurate since the last market trade might not be recently, and because individual trades don't necessarily reflect average market trends.

A related concept is the **model-implied price**, given when you plug in all your parameters to Black-Scholes or some other model. Traders compare this to the market price to decide if an option is fairly or unfairly priced. 

## Calculating volatility

**Volatility** measures how much the price of a stock fluctuates over time. It can be **historical/realised volatility** (computed from past price data), or **implied volatility** (the volatility value which, when plugged into Black-Scholes or some other model, produces the option's observed market price).

The way that historical volatility is computed is using log returns. Why? 

1. Volatility depends on how much stock prices change between points in time. 
2. You can't just use the difference between stock prices, as this will depend on the individual stock and is not an objective measure.
3. So you have to use the ratio, or **simple return**=$\frac{P_2-P1}{P_1}$ where $P_1$ is initial price and $P_2$ is final price. 
4. But now if you are considering returns over a period of time, you must multiply. Over $n$ periods, your total return will be $(1+R_1)\times (1+R_2)\times ...\times (1+R_n)-1$ where $R_i$ is the simple return for the $i^{th}$ period. 
5. This makes them inconvenient to work with. To calculate mean returns over a time period, the geometric mean must be used, which is computationally expensive. Multiplying is, computationally, a more difficult operation than addition. Finally, you can't assume that returns are normally distributed, which makes them harder to reason about statistically. 
6. So we need to go to something additive. How do we go from $\times$ to $+$? Logs, of course!
7. The **log return** over a period of time is $\ln{\frac{P_2}{P_1}}$. Over several periods, the total log return is $\sum \frac{P_{i+1}}{P_i}$. This is additive and easy to work with. A nice property - for small $x$, $\ln{1+x}\approx x$, which is to say that for small returns (as seen in everyday contexts) the log return is a good estimate for the simple return. 

Now given $n$ daily log returns with $r_i=\ln{\frac{P_i}{P_{i-1}}}$:

$\sigma=\sqrt{\frac{1}{n-1}\sum_{i=1}^n(r_t-\bar{r})^2}$, or sample standard deviation of log returns, is the realised volatility. 

If you want to find annual volatility, it will be higher than daily volatility, because as time goes on, uncertainty about where price could be increases. (This doesn't indicate that volatility of a market is always increasing; it just means that the longer your time interval, the higher your volatility will be.) In particular, assuming 252 trading days in a year, yearly volatility will be $\sigma_{\text{annual}} = \hat{\sigma} \times \sqrt{252}$, since $Var(r_1+...+r_n)=n\cdot Var(r_1)$ for i.i.d. $r_1,...,r_n$. 


## Brownian motion

Standard **Brownian motion** is a continuous-time stochastic process $W_t$ (reminder: a model for a system changing *randomly* over time, which can be denoted as a family of random variables, one for each time point) defined by three properties:

1. $W_0=0$ (at time zero, the variable )
2. **Independent increments** - $W_t-W_s$ is independent of $W_s-W_u$ for $u<s<t$ (memoryless property)
3. **Normally distributed increments** - $W_t-W_s\sim N(0,t-s)$

This reuslts in a random, continous path whose variance grows linearly in time, since:

Split $[0,t]$ into $n$ equal subintervals of length $\delta=t/n$. Each $W_{k\delta}​−W_{(k−1)\delta}$ is independent with variance $\delta$ (from (3)). Then $W_t-W_0$ is the sum of $n$ such increments, and since they are independent, its variance is $n$ times the variance of each increment, which is $\delta=t/n$, so its variance is just $t$; i.e. variance is linear in time (as explained above). 

Now this is standard Brownian motion. The increments have mean 0, so on average the random walk returns to the same place. Suppose now we have some **drift** term $\mu$ and some variable **volatility** $\sigma$. This can be defined as $X_t=\mu t + \sigma W_t$ where $W_t$ is a standard Brownian motion process. Since now $X_t-X_s=\mu(t-s)+\sigma(W_t-W_s)$, and since $\sigma(W_t-W_s)\sim N(0,\sigma^2(t-s))$, we get $X_t-X_s\sim N(\mu(t-s),\sigma^2(t-s))$. 

We can express this as a *stochastic differential equation* $dX_t=\mu dt + \sigma dW_t$. This solves to $X_t=X_0+\mu t + \sigma W_t$; i.e. the value after some time is the initial value, plus the constantly increasing drift term, plus a random term. You can think of this as $x_i=x_{i-1}+\delta+e$ where $\delta$ is some constant drift - it always goes up or down by some amount - and $e$ is the random noise component; a random walk with drift will tend, on average, upwards or downwards. In the context of a financial market, this means there is a constant *expected rate of return* $\mu$. Since $\sigma$ is also constant, the *volatility of returns* is also constant over time. 

Now this feels wrong because it implies that for *any* stock, no matter its initial price, the rate of return is constant at $\mu$. Empirical data shows that what's actually constant across differently prices stocks is *percentage rate of return*, differentially expressed as $\frac{dS_t}{dt}$. If we assume that *percentage returns* are instead modelled by Brownian motion, we get that $dS_t=\mu S_tdt+\sigma S_t dW_t$. Using Ito's lemma (dw about it...) we can get the fact that $d(\ln S_t)=(\mu - \frac{1}{2}\sigma^2)dt + \sigma dW_t$, or $\ln \frac{S_T}{S_0}=(\mu - \frac{1}{2}\sigma^2)T + \sigma W_t$, that is to say, log-returns are normally distributed: $\ln \frac{S_T}{S_0}\sim N((\mu-\frac{1}{2}\sigma^2)T,\sigma^2 T)$. 

In other words, $S_T=S_0e^{(\mu-\frac{1}{2}\sigma^2)T+\sigma W_t}$, where $W_t$ is a normal random variable.

This is **geometric Brownian motion** - it has the further properties that 

1. Instantaneous log-returns are normally distributed
2. Prices are log-normally distributed

This is useful as it ensures that prices can't fall below zero (log-normal distribution) and it assumes that percentage-based returns are i.i.d., which better matches how real markets move. 

## Black-Scholes formula

A theoretical estimate for the price of an option can be determined using the **Black-Scholes model**. Starting with a few assumptions:

1. The market consists of at least one risky asset (the **stock**) and one riskless asset (cash/bond).
2. The rate of return on the riskless asset is constant and referred to as the **risk-free interest rate**. 
3. The log return of the stock price at any instant is a random walk with drift. I.e., the stock price follows geometric Brownian motion. (This is useful because it keeps prices positive, has independent returns, )
4. There are no transaction costs or taxes.
5. Trading is continuous and short-selling (borrowing shares to immediately sell and then rebuy at a lower price later to return to the seller, pocketing the difference) is permitted. 

So we want to determine the price of an option. One way we can do so is by determining the price of a trading strategy with a payout equal to that of an option. One such strategy is having a portfolio with some option $C$ and $\Delta$ (unknown quantity) shares of stock which have been borrowed in order to short-sell, which currently has price $S$. Then $d\Pi=dC-\Delta dS$. (*Not sure why this works?*)

$dS=\mu Sdt+\sigma S dW$. Since $C$ is a function of $S$ and $t$, we can use Ito's lemma again (dw about it), which tells you that if $C$ is a function of a stochastic process $S$, then $dC=\frac{\delta C}{\delta t}dt+\frac{\delta C}{\delta S}dS + \frac{1}{2}\frac{\delta^2C}{\delta S^2}dS^2$. By subbing in our expression for $dS$ and subbing all that back in we get (just trust) that

$d\Pi=(\frac{\delta C}{\delta t}+\mu S \frac{\delta C}{\delta S} + \frac{1}{2}\sigma^2 S^2\frac{\delta^2 C}{\delta S^2}-\Delta \mu S)dt + \sigma S(\frac{\delta C}{\delta S}-\Delta)dW_t$. 

Now if we set $\Delta=\frac{\delta C}{\delta S}$, our portfolio will be a deterministic function of $t,S,\mu,\sigma,C$, and hence will be risk-free. Hence assuming no arbitrage, it should return the risk-free rate $r$, so $d\Pi =r\Pi dt$. Making that substitution and substituting in $\Pi=C-\Delta S=C-\frac{\delta C}{\delta S}S$ and equating we get

$\frac{\delta C}{\delta t}+rS\frac{\delta C}{\delta S}+\frac{1}{2}\sigma^2 S^2\frac{\delta^2 C}{\delta S^2}-rC=0$ ($dt$ terms cancel out) - this is the Black-Scholes PDE.

By considering that $C(S,T)=max(S_T-K,0)$ for a call and doing some changes of variables we derive the formula 

$C=S_0 N(d_1)-Ke^{-rT}N(d_2)$, 

$d_1=\frac{\ln{(S_0/K)}+(r+\frac{1}{2}\sigma^2)T}{\sigma \sqrt{T}}$,

$d_2=d_1-\sigma \sqrt{T}$.

For a put it's the same but $P=Ke^{-rT}N(-d_2)-S_0 N(-d_1)$.

## Interpreting these terms: 

$d_1$ is a measure of how many standard deviations the current stock price is above the strike price

$S_0N(d_1)$ 


# Regime-switching option pricing

Real financial markets do not have a single, stable volatility. They alternate between distinct **regimes** - usually we model a low-volatility bull market and a high-volatility bear market (the names are thought to come from the fact that bulls 'thrust their horns up - high rate of return, low volatility' to attack whereas bears 'swipe their paws down - low rate of return, high volatility'). A **regime-switching model** accounts for this by allowing the parameters of the price process (drift $\mu$, volatility $\sigma$) to change depending on some state variable $Z_t$.
 
## The model
 
Let $Z_t \in \{1, 2, \ldots, K\}$ be a discrete hidden Markov chain representing the current regime, governed by a **transition probability matrix** $\mathbf{A}$ where:
 
$$A_{ij} = P(Z_{t+1} = j \mid Z_t = i)$$
 
Stock prices are then modelled as GBM *conditional* on the current regime:
 
$$dS_t = \mu_{Z_t} S_t \, dt + \sigma_{Z_t} S_t \, dW_t$$
 
Each regime $k$ has its own drift $\mu_k$ and volatility $\sigma_k$. In a two-regime model, regime 1 might represent a calm market ($\sigma_1 = 0.15$) and regime 2 a turbulent market ($\sigma_2 = 0.40$).
 
## Option pricing under regime-switching
 
Pricing is more complex than in Black-Scholes because the hidden states mean you can't just set $\Delta$ to some value which makes the portfolio riskless, as you could always switch to a different state requiring a different $\Delta$. Several approaches exist:
 
- **Closed-form approximations** — for two-state Markov chains, you can actually just extend the Black-Scholes formula 
- **Risk-neutral pricing with regime risk** — the market is incomplete under regime-switching (the Markov chain is not a traded asset), so one must choose a pricing measure, typically by specifying how the market prices regime risk.
- **Monte Carlo simulation** — simulate paths of $(S_t, Z_t)$ jointly, compute the discounted payoff on each path, and average. Straightforward but slow.
- **PDE systems** — one Black-Scholes-like PDE per regime, coupled by the transition rates, solved simultaneously.

# HMMs + Background

## What is a Hidden Markov Model?

A **Hidden Markov Model** (HMM) is a statistical model in which the system being observed is assumed to be a Markov process with hidden states - that is to say, you can't tell just by observing the situation what state the system is in. However, each state does produce some observable outcome according to an **emission distribution**. It can be formally defined by
- A set of **hidden states** $Z = \{1, \ldots, K\}$
- A **transition matrix** $\mathbf{A}$, where $A_{ij} = P(Z_t = j \mid Z_{t-1} = i)$
- An **emission distribution** $B_k(\cdot) = P(X_t \mid Z_t = k)$ for each state $k$
- An **initial state distribution** $\pi_k = P(Z_1 = k)$

## HMMs in finance

In the regime-switching context, the state would be the market regime (bullish or bearish); the emission would be the observed log return on a particular day; the transition matrix contains probabilities of switching regimes; and the emission distribution is the probability of certain returns for each regime. 

## Problems to solve

1. **Evaluation**: Given an HMM model and a sequence of observations, calculate the probability that the model produced that sequence. 
2. **Deocding**: Given an HMM model and a sequence of observations, discover the most likely sequence of hidden states that produced those observations. 
3. **Learning**: Given an observation sequence and a set of states, find the HMM parameters ($A,B,\pi$) that maximise the likelihood of having seen those observations. 

(3) is the problem we are are solving, and it can be solved by the **Baum-Welch algorithm. **

# Baum-Welch algorithm

## Overview
 
Given a sequence of observations $X_{1:T}$, this algorithm finds parameters $\theta = (\mathbf{A}, \mathbf{B}, \pi)$ that locally maximise the log-likelihood $\log P(X_{1:T} \mid \theta)$. (Log-likelihood is used to transform many multiplied probabilities into a simple sum.)
 
Because the hidden states $Z_{1:T}$ are unobserved, you can't use direct maximum likelihood. EM resolves this by alternating between:
 
- **E-step** — compute the posterior distribution over hidden states given current parameters.
- **M-step** — update parameters to maximise the expected complete-data log-likelihood.
## Forward and backward variables
 
The algorithm requires two auxiliary quantities:
 
**Forward variable** $\alpha_t(k)$: the probability of observing $X_1, \ldots, X_t$ *and* being in state $k$ at time $t$:
 
$$\alpha_t(k) = P(X_1, \ldots, X_t,\, Z_t = k \mid \theta)$$
 
Computed recursively (forward pass):
 
$$\alpha_1(k) = \pi_k \cdot B_k(X_1), \qquad \alpha_t(k) = B_k(X_t) \sum_{j=1}^K \alpha_{t-1}(j) \, A_{jk}$$
 
**Backward variable** $\beta_t(k)$: the probability of the future observations $X_{t+1}, \ldots, X_T$ given being in state $k$ at time $t$:
 
$$\beta_t(k) = P(X_{t+1}, \ldots, X_T \mid Z_t = k,\, \theta)$$
 
Computed recursively (backward pass):
 
$$\beta_T(k) = 1, \qquad \beta_t(k) = \sum_{j=1}^K A_{kj} \, B_j(X_{t+1}) \, \beta_{t+1}(j)$$
 
## E-step: posterior state probabilities
 
From $\alpha$ and $\beta$, compute:
 
**State occupancy** $\gamma_t(k) = P(Z_t = k \mid X_{1:T}, \theta)$:
 
$$\gamma_t(k) = \frac{\alpha_t(k)\,\beta_t(k)}{\sum_{j=1}^K \alpha_t(j)\,\beta_t(j)}$$
 
**Transition occupancy** $\xi_t(j, k) = P(Z_t = j, Z_{t+1} = k \mid X_{1:T}, \theta)$:
 
$$\xi_t(j,k) = \frac{\alpha_t(j)\, A_{jk}\, B_k(X_{t+1})\, \beta_{t+1}(k)}{\sum_{j'}\sum_{k'} \alpha_t(j')\, A_{j'k'}\, B_{k'}(X_{t+1})\, \beta_{t+1}(k')}$$
 
## M-step: parameter updates
 
Re-estimate parameters using the soft state assignments from the E-step:
 
$$\hat{\pi}_k = \gamma_1(k)$$
 
$$\hat{A}_{jk} = \frac{\sum_{t=1}^{T-1} \xi_t(j,k)}{\sum_{t=1}^{T-1} \gamma_t(j)}$$
 
For Gaussian emissions ($B_k = \mathcal{N}(\mu_k, \sigma_k^2)$):
 
$$\hat{\mu}_k = \frac{\sum_{t=1}^T \gamma_t(k)\, X_t}{\sum_{t=1}^T \gamma_t(k)}, \qquad \hat{\sigma}_k^2 = \frac{\sum_{t=1}^T \gamma_t(k)\,(X_t - \hat{\mu}_k)^2}{\sum_{t=1}^T \gamma_t(k)}$$
 
## Convergence
 
The E and M steps are repeated until the log-likelihood $\log P(X_{1:T} \mid \theta)$ converges (changes by less than some tolerance $\varepsilon$). Each iteration is guaranteed to increase or maintain the likelihood, so the algorithm converges to a **local maximum**. Multiple random initialisations are typically used to avoid poor local optima.
 
## Complexity
 
Each iteration costs $O(K^2 T)$ time (dominated by the forward-backward passes), where $K$ is the number of states and $T$ is the number of observations. For two-regime models ($K = 2$) applied to a year of daily returns ($T \approx 252$), this is extremely fast.
 
## Application to regime-switching option pricing
 
Once Baum-Welch has converged:
 
1. **Decoded regimes** — use the Viterbi algorithm to find $Z_{1:T}^*$, the most likely regime at each historical date.
2. **Calibrated parameters** — $\hat{\mu}_k$ and $\hat{\sigma}_k$ give per-regime drift and volatility; $\hat{\mathbf{A}}$ gives switching probabilities.
3. **Current regime probability** — $\gamma_T(k)$ gives a soft estimate of which regime the market is in *right now*.
4. **Option pricing** — feed the calibrated parameters into a regime-switching pricing formula or Monte Carlo to get option prices that reflect the possibility of future regime switches.
