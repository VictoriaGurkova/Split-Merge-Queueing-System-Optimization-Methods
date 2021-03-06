### Q-learning

**Q-learning** — метод, применяемый в искусственном интеллекте при агентном подходе. Относится к экспериментам вида *oбучение с подкреплением*. 
На основе получаемого от среды вознаграждения агент формирует функцию полезности **Q**, что впоследствии дает ему возможность уже не случайно выбирать стратегию поведения, а учитывать опыт предыдущего взаимодействия со средой.

### Алгоритм Q-learning

1. Initialization:
    1. `for each s and a do Q[s, a] = default` (RND or const=0) — инициализация функции полезности **Q** от действия **a** в ситуации **s** как случайную или константу для любых входных данных

2. Observe:
    1. `s' = s` — запомнить предыдущие состояния
    2. `a' = a` — запомнить предыдущие действия
    3. `s = get_current_state()` — получить текущие состояния
    4. `r = get_reward` — получить вознаграждение за предыдущее действие

3. Update:
    1. `Q[s', a'] = Q[s', a'] + LF * (r + DF * MAX(Q, s) - Q[s', a'])`

4. Decision:
    1. `a = ARGMAX(Q, s)`
    2. `TO_ACTIVATOR = a`
    
5. Repeat:
    1. `GO TO 2`
    

#### Обозначения 
- LF — фактор обучения. Чем он выше, тем сильнее агент доверяет новой информации
- DF — фактор дисконтирования. Чем он меньше, тем меньше агент задумывается о выгоде от будущих своих действий

#### Функция MAX(Q, s)
1. `max = minValue`

2. `for each a of ACTIONS(s) do`
    1. `if Q[s, a] > max then max = Q[s, a]`

3. `return max`

#### Функция ARGMAX(Q, s)
1. `amax = First of ACTION(s)`

2. `for each a of ACTION(s) do`
    1. `if Q[s, a] > Q[s, amax] them amax = a`

3. `return amax`
