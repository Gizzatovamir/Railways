
## All methods list with some information

![image of switch](../images/switch_demonstration.png "Title")

## Multiple point methods
#### Method 1

min(sum(sin(alpha_i)))

![img_3.png](../images/img_3.png)

[comment]: (\min_N\sum_{i=0}^n{\sin{\alpha_{i}}})

#### Method 2

min(sum(H_i))

![img.png](../images/img.png)

[comment]: (\min_N\sum_{i=0}^n{H_i})

#### Method 3

min(sum(sin(beta_i)) == sum(pi-sin(alpha_i)))

![img.png](../images/img_2.png)

[comment]: (\min_N\sum_{i=0}^n{\sin{\(\pi-\alpha_{i}\)}})

#### Method 4

min(sum(L_i * H_i))

![img_4.png](../images/img_4.png)

[comment]: (\min_N\sum_{i=0}^n{L_i\cdotH_i})

#### Method 5

min(sum(H/(L * (i + 1))))

![img_5.png](../images/img_5.png)

[comment]: (\min_N\sum_{i=0}^n{\frac{H_i}{L_i\cdot\(i+1\)}})

#### Method 6

min(sum(H * i))

![img_6.png](../images/img_6.png)

[comment]: (\min_N\sum_{i=0}^n{H_i\cdot\(i\)})

#### Method 8

min(sum(H * (i + 1)/L ))

![img.png](../images/img_8.png)

[comment]: (\min_N\sum_{i=0}^n{\frac{H_i\cdot\(i+1\)}{L_i}})

## Single point methods

#### method 7

![img_7.png](../images/img_7.png)


min(H_(n))

N = 0,1
n = len(gps_point_list)


[comment]: (\min_N\(H_{n}\))