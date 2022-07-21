# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 10:00:51 2022

@author: Administrator
"""

import random

def avg(lst,k = 1):
    n = len(lst)
    s = 0.1
    if n != 0:
        for i in lst:
            s += i**k
        return s/n
    else:
        return s
    
def resonable(lst1,lst2):
    #判断细胞收支是否符合物质守恒
    if sum(lst1)>sum(lst2):
        return True
    else:
        return False
    
def output(world,position,lst):
    x,y = position
    a = world[x][y][1]  #a为x，y处的环境
    l = len(world) #培养皿的边长
    for i in range(len(a)):
        a[i] += 0.6*lst[i]
    for i in [[-1,0],[1,0],[0,-1],[0,1]]:
        x1 = x + i[0]
        y1 = y + i[1]
        if x1 >= 0 and x1 < l and y1 >=0 and y1 < l:
            a = world[x1][y1][1]
            for i in range(len(a)):
                a[i] += 0.1*lst[i]



class Cell:
    def __init__(self,position,generation,what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance,born_rate,
             age = 50,grow_up_speed = 1,
             base_hp = 20):
        delta1 = 1e9 / 2
        self.position = position
        self.gen = generation
        self.need = what_it_need
        self.out = what_it_give
        self.bear = how_much_can_it_bear
        self.resist = resistance
        self.stress_resistance = stress_resistance
        self.bornrate = born_rate
        self.grow_speed = (avg(what_it_need)-avg(what_it_give))/avg(how_much_can_it_bear,2)*avg(resistance,2)*grow_up_speed/base_hp
        self.age = 1
        self.maxage = age/self.grow_speed**2/delta1
        self.grow_up_age = self.maxage*0.5/grow_up_speed
        self.hp = base_hp
        self.basehp = base_hp
        #print(self.maxage,self.grow_up_age)
    
    def grow(self,environment):
        s=0
        for i in range(len(self.need)):
            if self.bear[i] < environment[i]:
                s += (environment[i]-self.bear[i]) * self.resist[i] / len(self.need)
            if self.need[i] <= environment[i]:
                environment[i] -= self.need[i]
            else:
                s += (self.need[i] - environment[i])
                environment[i] = 0
        s *= 0.2
        '''if s != 0:
            print(s)'''
        self.hp -= s * self.basehp
        if s <= self.stress_resistance:
            self.age += 1
            self.hp += self.basehp
        global world
        output(world,self.position,self.out)
        if self.hp <= 0 or self.age > self.maxage:
            #print(self.hp <= 0)
            #print(self.age > self.maxage)
            self.die()
        
    def die(self):
        global world
        x,y = self.position
        world[x][y][0] = None
        #print('oh no!{}'.format(self.position))  #死了记得吱一声
        
    def evolve(self,evolve_speed = 1):
        global evolve_size
        random.seed()
        what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance=[],[],[],[],self.stress_resistance
        def randnum(evolve_size):return evolve_size*(random.random()-0.5)
        for i in range(len(self.need)):
            what_it_need.append(max(self.need[i]+randnum(evolve_size), 0))
            what_it_give.append(max(self.out[i]+randnum(evolve_size), 0))
            how_much_can_it_bear.append(self.bear[i]+randnum(evolve_size) * 0.5)
            resistance.append(max(self.resist[i]+randnum(evolve_size) , -0.05))
        stress_resistance += randnum(evolve_size)
        born_rate = (self.bornrate + randnum(evolve_size)) % 10 
        base_hp = self.basehp + randnum(evolve_size)
        has_place = len(count_genes(world)) < 10  #只有当前基因种类不超过10时才可以演化(可根据培养皿大小适当调节)
        if not resonable(what_it_need,what_it_give) or not has_place:
            global days
            print('day{},{}于{}演化失败'.format(days,self.gen,self.position))
            return self.gen,self.need,self.out,self.bear,self.resist,self.stress_resistance,self.bornrate,50,1,self.basehp
        global family_tree
        a = family_tree
        for g in self.gen:
            a = a[g]
        a.append([])
        return self.gen+[len(a)-1],what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance,born_rate,50,1,base_hp
    
    def is_adult(self):
        return self.age > self.grow_up_age