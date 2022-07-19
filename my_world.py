# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 12:31:33 2022

@author: Administrator
"""
#细胞-------------------------
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
    
def output(world,position,lst,cell_type):
    global base_damage_factor,base_heal_factor
    x,y = position
    environment = world[x][y][1]  #a为x，y处的环境
    l = len(world) #培养皿的边长
    for i in range(len(environment)):
        environment[i] += 0.6*lst[i]
    for i in [[-1,0],[1,0],[0,-1],[0,1]]:
        x1 = x + i[0]
        y1 = y + i[1]
        if x1 >= 0 and x1 < l and y1 >=0 and y1 < l:
            cell,environment = world[x1][y1]
            for i in range(len(environment)):
                environment[i] += 0.1*lst[i]
            if cell != None:  #此处计算该细胞对附近4个细胞的伤害（或治疗）
                delta = (cell.type-cell_type) % 5
                delta = min(delta,5-delta)
                if delta <= 1:
                    cell.do_damage((delta-1)*(6 - cell_type)/6*base_heal_factor)
                else:
                    cell.do_damage((delta-1)*(3 + cell_type)/8*base_damage_factor)



class Cell:
    def __init__(self,position,generation,what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance,born_rate,
             age = 50,grow_up_speed = 1,
             base_hp = 20,cell_type = 1):
        
        delta1 = 2500
        delta2 = 1  #两个值都是用来调节寿命的
        
        self.position = position
        self.gen = generation
        self.need = what_it_need
        self.out = what_it_give
        self.bear = how_much_can_it_bear
        self.resist = resistance
        self.stress_resistance = stress_resistance
        self.bornrate = born_rate
        self.age = 1
        self.maxage = age / (avg(what_it_need)-avg(what_it_give)) / avg(how_much_can_it_bear,2)*avg(resistance,2) / grow_up_speed / base_hp * delta1
        self.maxage = min(self.maxage , 50)
        self.grow_up_age = self.maxage / avg(what_it_need) / grow_up_speed * delta2
        self.hp = base_hp
        self.basehp = base_hp
        self.type = cell_type
        #print(self.maxage,self.grow_up_age)
        #input()
    
    def grow(self,environment):
        s=0
        for i in range(len(self.need)):
            if self.bear[i] < environment[i]:
                s += (environment[i]-self.bear[i]) * self.resist[i] / len(self.need)
            if self.need[i] <= environment[i]:
                environment[i] -= self.need[i]
            else:
                s += (self.need[i] - environment[i]) * 5
                environment[i] = 0
        s *= 0.2
        '''if s != 0:
            print(s)'''
        self.hp -= s * self.basehp
        
        self.age += 1
        if s <= self.stress_resistance:
            self.hp += self.basehp
        else:
            self.grow_up_age += 1
        global world
        output(world,self.position,self.out,self.type)
        if self.hp <= 0 or self.age > self.maxage:
            #print(self.hp <= 0)
            #print(self.age > self.maxage)
            self.die()
        
    def die(self):
        global world,days,f2,basic_damage_days,cell_lst
        x,y = self.position
        world[x][y][0] = None
        l = len(world)
        environment = world[x][y][1]
        if not self.is_adult():
            return
        global base_nutrition_factor
        nutrition_delta = 2 * min(self.age / (self.grow_up_age + 1) , 0.5) * base_nutrition_factor
        for i in range(len(environment)):  #死后向周围释放营养物质
            environment[i] += 0.6 * nutrition_delta * self.out[i]
            for i in [[-1,0],[1,0],[0,-1],[0,1]]:
                x1 = x + i[0]
                y1 = y + i[1]
                if x1 >= 0 and x1 < l and y1 >= 0 and y1 < l:
                    environment = world[x1][y1][1]
                    for i in range(len(environment)):
                        environment[i] += 0.1 * nutrition_delta * self.out[i]
        #print('{} die'.format(self.position))  #死了记得吱一声
        
    def evolve(self,evolve_speed = 1):
        global evolve_size
        random.seed()
        what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance=[],[],[],[],self.stress_resistance
        def randnum(evolve_size):return evolve_size*(random.random()-0.5)
        for i in range(len(self.need)):
            what_it_need.append(max(self.need[i]+randnum(evolve_size) * 2, 0))
            what_it_give.append(max(self.out[i]+randnum(evolve_size) * 2, 0))
            how_much_can_it_bear.append((self.bear[i]+randnum(evolve_size) * 10) % 50)
            resistance.append(max(self.resist[i]+randnum(evolve_size) * 0.5 , 0.02))
        stress_resistance += randnum(evolve_size) * 10
        born_rate = (self.bornrate + randnum(evolve_size) * 2) % 10 
        base_hp = self.basehp + randnum(evolve_size) * 5
        cell_type = (self.type + randnum(evolve_size) * 2) % 5
        has_place = len(count_genes(world)) < 10  #只有当前基因种类不超过10时才可以演化(可根据培养皿大小适当调节)
        if not resonable(what_it_need,what_it_give) or not has_place:
            global days
            #print('day{},{}于{}演化失败'.format(days,self.gen,self.position))
            return self.gen,self.need,self.out,self.bear,self.resist,self.stress_resistance,self.bornrate,50,1,self.basehp,self.type
        global family_tree
        a = family_tree
        for g in self.gen:
            a = a[g]
        a.append([])
        return self.gen+[len(a)-1],what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance,born_rate,50,1,base_hp,cell_type
    
    def is_adult(self):
        return self.age > self.grow_up_age
    
    def do_damage(self,damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()
    
    
#世界规则-------------------------
nutrition = [0.5]*50
basic_ratio = 1
ratio = basic_ratio
evolve_rate = 10  #变异速率
evolve_size = 2  #变异幅度
born_cost = 1  #繁殖代价系数

damage_ratio = 2500  #天灾出现天数


def step(world):
    global nutrition , ratio , disaster_name , days , damage_ratio , damage_days
    for i in range(len(world)):
        for j in range(len(world[i])):
            cell,environment = world[i][j]
            if cell != None:
                cell.grow(environment)
            else:
                born(i,j)
            for k in range(len(environment)):  #营养会趋向20至30之间
                if environment[k] < 20:
                    environment[k] += nutrition[k]*ratio
                elif environment[k] > 30:
                    environment[k] -= nutrition[k]*ratio
                if environment[k] > 100:  #最大值设为100
                    environment[k] = 100
                elif environment[k] < 0:
                    environment[k] = 0
    
    if days % damage_ratio == 0:
        disaster()
    else:
        if damage_days == 0:
            stop_damage()
        elif disaster_name != None:
            disaster_name()


def count_genes(world):  #数数有几种个体
    lst=[]
    for i in world:
        for j in i:
            cell = j[0]
            if cell != None:
                gene = cell.gen
                if gene not in lst:
                    lst.append(gene)
    return lst

def born(i,j):  #繁殖
    global world,evolve_rate,born_cost
    l = len(world) #培养皿的边长
    for k in [-1,0,1]:
        for h in [-1,0,1]:
            x = i + k
            y = j + h
            ran = random.random()*100
            if x >= 0 and x < l and y >=0 and y < l:
                cell = world[x][y][0]
                if cell != None and cell.is_adult() and cell.hp > cell.basehp * born_cost:
                    #print(cell.age,cell.grow_up_age,cell.is_adult())
                    ran -= cell.bornrate * born_cost
                    if ran <= 0:
                        #print('new life',ran,i,j)
                        #input()
                        cell.do_damage(cell.basehp)
                        if ran < -evolve_rate * (3-k**2-h**2) / 200:  #符合条件是演化，否则正常繁殖
                            world[i][j][0] = Cell([i,j],cell.gen,cell.need,cell.out,cell.bear,cell.resist,cell.stress_resistance,cell.bornrate,
                                                  50,1,
                                                  cell.basehp,cell.type)
                        else:
                            world[i][j][0] = Cell([i,j],*cell.evolve())
                        return
        


#天灾-------------------------
basic_damage_days = 100  #天灾持续天数
basic_damage_level = 2  #初始天灾级别
damage_days = 0  #当前天灾剩余天数
damage_level = 0

base_damage_factor = 1
base_heal_factor = 1
base_nutrition_factor = 1

disaster_name = None #

def disaster():
    global days,damage_ratio,basic_damage_days,basic_damage_level,damage_days,damage_level,disaster_name,damage_level
    damage_level = max(basic_damage_level , random.randint(min(max(0,days // damage_ratio-2),3), min(5 , 1 + days // damage_ratio)))
    damage_days = random.randint(basic_damage_days // 2, basic_damage_days * 2)
    disaster_lst = [frame, barren, fertile, eutrophic, death, posion,violent,degrade,dystocia]  #天灾集合，静待选购
    
    disaster_name = disaster_lst[random.randint(0,len(disaster_lst)-1)]
    s = disaster_name()
    if damage_days == 0:
        s = 'day {}, disaster {}, danger level {}'.format(days,s, damage_level)
    else:
        s = 'day {}, disaster {}, danger level {}, lasting for {} days'.format(days,s, damage_level, damage_days)
    global f2
    f2.write(s + '\n')
    print(s)

def stop_damage():
    global disaster_name,damage_level
    damage_level = 0
    if disaster_name != None:
        disaster_name()
        disaster_name = None
    

#注：部分事件不受持续天数影响
def frame():  #饥荒，自然回复率降低
    global ratio,basic_ratio,damage_level
    ratio = basic_ratio / (1 + 0.5 * damage_level)
    return 'frame'
    


def barren():  #贫瘠，营养降低
    global world,damage_days,damage_level,disaster_name
    damage_days = 0
    disaster_name = None
    l = len(world)
    for x in range(l):
        for y in range(l):
            environment = world[x][y][1]
            for i in range(len(environment)):
                environment[i]=(0 * damage_level + environment[i] * (5 - damage_level)) / 5
    return 'barren'


def fertile():  #丰饶，自然恢复增加
    global ratio,basic_ratio,damage_level
    ratio = basic_ratio * (1 + 0.5 * damage_level)
    
    return 'fertile'

def eutrophic():  #富营养，营养增加
    global world,damage_days,damage_level,disaster_name
    damage_days = 0
    disaster_name = None
    l = len(world)
    for x in range(l):
        for y in range(l):
            environment = world[x][y][1]
            for i in range(len(environment)):
                environment[i]=(50 * damage_level + environment[i] * (5 - damage_level)) / 5
    return 'eutrophic'

def death():  #死亡，随机击杀细胞
    global world,damage_days,damage_level,disaster_name
    damage_days = 0
    disaster_name = None
    l = len(world)
    for i in range(l*l*damage_level):
        x = random.randint(0, l-1)
        y = random.randint(0, l-1)
        world[x][y][0] = None
    return 'death'

def posion():  #剧毒，损失生命
    global world,damage_level,damage_days
    damage_days = damage_days
    l = len(world)
    damage = 3 * damage_level  #这里填5的话细胞在5级天灾下可能会死得很惨
    for x in range(l):
        for y in range(l):
            cell = world[x][y][0]
            if cell != None:
                cell.do_damage(damage)
    return 'posion'

def violent():  #狂暴，治疗量降低，伤害增加
    global base_damage_factor,base_heal_factor,damage_level
    base_damage_factor = 1 + 0.5 * damage_level
    base_heal_factor = 1 - 0.3 * damage_level
    
    return 'violent'

def degrade():  #降解，细胞死后产生更多营养
    global base_nutrition_factor,damage_level
    base_nutrition_factor = 1 + damage_level
    
    return 'degrade'

def dystocia():  #难产，繁殖代价提升
    global born_cost,damage_level
    born_cost = 1 + 0.5 * damage_level
    
    return 'dystocia'

#-------------------------
from PIL import Image
import os

def gene_to_color(gene):
    a = 1
    for i in gene:
        a *= (i+1) * 10
    return a % (256**3-1)



def print_the_world(world,factor = 1):
    l = len(world)
    im = Image.new('RGB',(l,l))
    for i in range(len(world)):
        for j in range(len(world)):
            cell = world[i][j][0]
            if cell == None:
                color = 256**3-1
            else:
                color = gene_to_color(cell.gen)
            im.putpixel((i,j),color)
    
    global days
    img = im.resize((l*5,l*5))
    img.save('image/day{}.gif'.format(days * factor),'GIF')



world = []
environment = [10]*10  #初始环境（可调节）
family_tree = []
try:
    os.mkdir('image')
except:
    pass


for i in range(50):
    l = []
    for j in range(50):
        l.append([None,environment.copy()])
    world.append(l)


#始祖细胞配制（可调）（但别tm瞎调这个细胞，尤其是那个抗性，分分钟暴毙）
what_it_need = [2]*10
what_it_give = [1.5]*10
how_much_can_it_bear = [25]*10
resistance = [1]*10
stress_resistance = 50
born_rate = 5


for i in range(3):
    for j in range(3):
        world[10+i][3+j][0] = Cell([10+i,3+j],[],what_it_need,what_it_give,how_much_can_it_bear,resistance,stress_resistance,born_rate,
             age = 50,grow_up_speed = 1,
             base_hp = 20,cell_type = 3)
#初始化培养皿

days = 1  #实验天数
always_print = False

f2 = open('image/disaster.txt','w')
while days<50000:
    step(world)
    #print(count_genes(world))
    days+=1
    if len(count_genes(world))==0:
        #pass
        print('end at {}'.format(days))
        break
    if days % 100 == 0:
        print(count_genes(world))
        if always_print:
            print_the_world(world,0)
        elif days % 500 == 0:
            print(days)
            print_the_world(world)


lst=[]
f = open('image/cells.txt','w')
for i in world:
    for j in i:
        cell = j[0]
        if cell != None:
            gene = cell.gen
            if gene not in lst:
                lst.append(gene)
                f.write('gen={},need={},out={},bear={},resist={},stress={},bornrate={},baseage={},grow={},hp={},cell_type={}\n'.format(cell.gen,cell.need,cell.out,cell.bear,cell.resist,cell.stress_resistance,cell.bornrate,50,1,cell.basehp,cell.type))
                f.write(str([cell.gen,cell.need,cell.out,cell.bear,cell.resist,cell.stress_resistance,cell.bornrate,50,1,cell.basehp,cell.type]))
                f.write('\n\n')
f.close()
f2.close()