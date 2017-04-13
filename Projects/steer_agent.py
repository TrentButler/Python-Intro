from Tools._MathLib import Vector2
from FSM._FSM import _FSM
from AGENT._agent import Agent
import random
import math
import os # DEBUG USE

class SteerAgent(Agent):
    '''STEER AGENT'''

    def __init__(self, name):
        super(SteerAgent, self).__init__(name)
        self._state_machine = _FSM()
        self._current = None

        self._state_machine.AddState('INIT')
        self._state_machine.AddState('IDLE')
        self._state_machine.AddState('SEEK')
        self._state_machine.AddState('FLEE')
        self._state_machine.AddState('WANDER')

        self._state_machine.AddTransition(('INIT', 'IDLE'))
        self._state_machine.AddTransition(('IDLE', 'SEEK'))
        self._state_machine.AddTransition(('IDLE', 'FLEE'))
        self._state_machine.AddTransition(('IDLE','WANDER'))
        self._state_machine.AddTransition(('SEEK', 'IDLE'))
        self._state_machine.AddTransition(('SEEK', 'FLEE'))
        self._state_machine.AddTransition(('SEEK', 'WANDER'))
        self._state_machine.AddTransition(('FLEE', 'IDLE'))
        self._state_machine.AddTransition(('FLEE', 'SEEK'))
        self._state_machine.AddTransition(('FLEE', 'WANDER'))
        self._state_machine.AddTransition(('WANDER', 'IDLE'))
        self._state_machine.AddTransition(('WANDER', 'SEEK'))
        self._state_machine.AddTransition(('WANDER', 'FLEE'))
        
        self._state_machine.StartMachine('INIT')
        self._random = random
    
    def _init(self, posVec, max_vel, mass):
        self._position = posVec
        self._velocity = Vector2(0, 0)
        self._max_velocity = max_vel
        self._heading = Vector2(0, 0)
        self._mass = mass
        self._size = mass * 20
        self._force = Vector2(0, 0)
        self._wanderang = math.pi / 4
        self._wandercirc = SteerAgent(self._name + "(" + "wander" + ")")
        self._hitbox = []
        
    def _seek(self, target):
        '''CREATE A DISPLACEMENT VECTOR USING A TARGET, RETURN THAT FORCE'''
        displacement = self._getdist(target) # CREATE AN DISPLACEMENT VECTOR FROM A-B
        V = displacement.norm() * self._max_velocity # NORMALIZE THE DISPLACEMENT, SCALE BY AGENT MAX VELOCITY
        force = V - self._velocity # SUBTRACT DISPLACEMENT VECTOR FROM AGENT CURRENT VELOCITY, TO GET FORCE REQUIRED TO CHANGE AGENT DIRECTION
        return force # RETURN FORCE

    def _flee(self, target):
        '''CREATE A DISPLACEMENT VECTOR USING A TARGET, RETURN THAT FORCE'''
        displacement = target._getdist(self) # CREATE AN DISPLACEMENT VECTOR FROM A-B
        V = displacement.norm() * self._max_velocity # NORMALIZE THE DISPLACEMENT, SCALE BY AGENT MAX VELOCITY
        force = V - self._velocity # SUBTRACT DISPLACEMENT VECTOR FROM AGENT CURRENT VELOCITY, TO GET FORCE REQUIRED TO CHANGE AGENT DIRECTION
        return force # RETURN FORCE
    
    def _wander(self, rad, dist, strength):
        '''CREATE A DISPLACEMENT VECTOR USING A CIRCLE A DISTANCE FROM AGENT, RETURN THAT FORCE'''
        os.system("cls")
        print self._name + str(self._getpos())

        origin = self._velocity.norm() # NORMALIZE VELOCITY TO MAKE SURE THE CIRCLE'S ORIGIN IS IN FRONT OF AGENT
        origin = origin * dist # SCALE ORIGIN BY DISTANCE
        displacement = Vector2(self._random.randint(0, strength), random.randint(0, strength)) # CREATE A DISPLACEMENT VECTOR
        self._wanderang = self._wanderang + (self._random.random() * 1) - (1 * .5) # MATH ON AGENT'S WANDER ANGLE TO GET RANDOM ANGLE
        displacement._x = math.cos(self._wanderang) * displacement.mag() # DO COS(ANGLE) FOR DISPLACEMENT VECTOR X, SCALE BY THE MAGNITUDE OF THE DISPLACEMENT VECTOR
        displacement._y = math.sin(self._wanderang) * displacement.mag() # DO SIN(ANGLE) FOR DISPLACEMENT VECTOR Y, SCALE BY THE MAGNITUDE OF THE DISPLACEMENT VECTOR
        displacement = displacement + origin # ADD ORIGIN TO THE DISPLACEMENT, 

        target = SteerAgent('target')
        target._init(displacement + self._position, 0, 0)   
        self._wandercirc = target
        V = displacement.norm() * self._max_velocity # NORMALIZE THE DISPLACEMENT, SCALE BY AGENT MAX VELOCITY
        force = V - self._velocity # SUBTRACT DISPLACEMENT VECTOR FROM AGENT CURRENT VELOCITY, TO GET FORCE REQUIRED TO CHANGE AGENT DIRECTION
        return force # RETURN FORCE
        
    def _getpos(self):
        '''RETURNS TUPLE'''
        return (self._position._get_x(), self._position._get_y())
    
    def _getdist(self, target):
        # _xdist = self._getpos()[0] - target._getpos()[0]
        _xdist = target._getpos()[0] - self._getpos()[0]
        # _ydist = self._getpos()[1] - target._getpos()[1]
        _ydist = target._getpos()[1] - self._getpos()[1]
        return Vector2(_xdist, _ydist)
    def _dist(self, target):
        xdist = abs(self._position._get_x() - target._position._get_x())
        ydist = abs(self._position._get_y() - target._position._get_y())
        return xdist + ydist
    
    def _choice(self, start, stop):
        # x = random.randint(int(start._get_x()), int(stop._get_x()))
        # y = random.randint(int(start._get_y()), int(stop._get_y()))

        x = random.uniform(start._get_x(), stop._get_x())
        y = random.uniform(start._get_y(), stop._get_y())

        return Vector2(x, y)
    
    def _run(self, deltaTime, target):
        if super(SteerAgent, self)._run():
            self._current = self._state_machine.currentstate

            topleft = self._position + Vector2(-self._mass, self._mass)
            bottomright = self._position + Vector2(self._mass, -self._mass)

            self._hitbox = [topleft, bottomright]
            self._hitbox = [self._position._get_x(), self._position._get_y(), self._size, self._size]

            if self._current is 'INIT':
                self._state_machine.ChangeState('IDLE')

            if self._current is 'IDLE':
                accel = self._force * self._mass
                self._velocity = self._velocity + (accel * deltaTime)
                # self._force = Vector2(0, 0)

                # print self._name, self._heading._get_x(), self._heading._get_y()          
                # print "IDLE STATE"

            if self._current is 'SEEK':
                self._force = self._seek(target)
                accel = self._force * self._mass
                self._velocity = self._velocity + (accel * deltaTime)
                # self._force = Vector2(0, 0)

                print self._name, self._heading._get_x(), self._heading._get_y()
                # print "SEEK STATE"

            if self._current is 'FLEE':
                self._force = self._flee(target)
                accel = self._force * self._mass
                self._velocity = self._velocity + (accel * deltaTime)
                # self._force = Vector2(0, 0)
                # print self._name, self._heading._get_x(), self._heading._get_y()
                # print "FLEE STATE"

            if self._current is 'WANDER':
                self._force = self._wander(600, 80, 20)
                accel = self._force * self._mass
                self._velocity = self._velocity + (accel * deltaTime)
                # self._force = Vector2(0, 0)

                # print self._name, self._heading._get_x(), self._heading._get_y()
                # self._wandercirc = self._wander(60, 100, 45, 2)
                # print "WANDER"
            
            self._position = self._position + (self._velocity * deltaTime)
            self._heading = self._velocity.norm()
            self._force = Vector2(0, 0)

