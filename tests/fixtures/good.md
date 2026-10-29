# [백준 1920] 수 찾기

## 문제

<!-- 문제 원문 붙여넣기 -->

출처: [백준 1920](https://www.acmicpc.net/problem/1920)

## 생각한 흐름

- N개를 리스트에 넣는다
- M개를 하나씩 보면서 `in`으로 리스트에 있는지 확인
- 있으면 1, 없으면 0 출력

## 틀린 코드

```python
n = int(input())
cards = list(map(int, input().split()))
m = int(input())
for x in map(int, input().split()):
    print(1 if x in cards else 0)
```

예제는 다 맞았는데 제출하니까 시간 초과가 났다.

## 리스트 in이 느렸던 이유

반복문이 하나밖에 없어서 왜 느린지 감이 안 왔다. 찾아보니 리스트에서 `in`은 앞에서부터 하나씩 비교한다. 눈에 보이는 반복문은 하나지만 `in` 안에 반복문이 하나 더 숨어 있었던 거다.

`set`은 해시로 위치를 바로 계산해서 하나씩 비교하지 않는다. 출력도 한 줄씩 `print`하는 것보다 모아서 한 번에 하는 게 빠르다.

## 정답 코드

```python
import sys
input = sys.stdin.readline

n = int(input())
cards = set(map(int, input().split()))
m = int(input())
out = []
for x in map(int, input().split()):
    out.append("1" if x in cards else "0")
print("\n".join(out))
```

## 돌아보며

**왜 막혔을까**

- 반복문이 하나니까 괜찮겠지 하고, `in`이 안에서 하나씩 비교한다는 걸 생각하지 않은 점
- 같은 자료에서 10만 번을 찾는데 리스트를 그대로 쓴 점

리스트 `in`이 느리다는 얘기는 들어본 것 같은데, 막상 코드를 쓸 때는 떠오르지 않았다. 다음부터는 같은 자료에서 여러 번 찾는 코드가 보이면 `in` 앞에 있는 게 리스트인지 먼저 확인해 볼 생각이다.
