from amaranth import *
from amaranth.build import *

class Timer(Elaboratable):
    def __init__(self, pins):
        self.en = Signal(1)                 # enable
        self.cnt = Signal(16)               # timer value
        self.arr = Signal(16)               # reload value
        self.ccr = Signal(16)
        self.dir = Signal(1)                # only used for center-aligned, 0 up 1 down
        self.psc = Signal(4)                # prescaler
        self.alignment = Signal(2)          # 0 up, 1 down, 2 center-aligned, 3 xxx

        self.pins = pins

    def elaborate(self, platform):
        m = Module()

        with m.If(self.en == 1):


            with m.Switch(self.alignment):
                with m.Case(0): # Up
                    m.d.sync += self.dir.eq(0)

                    with m.If(self.cnt < self.ccr):
                        m.d.sync += self.pins.eq(0)
                    with m.Else():
                        m.d.sync += self.pins.eq(1)

                    with m.If(self.cnt < self.arr):
                        m.d.sync += self.cnt.eq(self.cnt + 1)
                    with m.Else():
                        m.d.sync += self.cnt.eq(0)

                with m.Case(1): # Down
                    m.d.sync += self.dir.eq(1)

                    with m.If(self.cnt < self.ccr):
                        m.d.sync += self.pins.eq(1)
                    with m.Else():
                        m.d.sync += self.pins.eq(0)

                    with m.If(self.cnt != 0):
                        m.d.sync += self.cnt.eq(self.cnt - 1)
                    with m.Else():
                        m.d.sync += self.cnt.eq(self.arr)


                with m.Case(2): # Center-aligned
                    with m.Switch(self.dir):
                        with m.Case(0): # Counting up
                        
                            with m.If(self.cnt < self.ccr):
                                m.d.sync += self.pins.eq(0)
                            with m.Else():
                                m.d.sync += self.pins.eq(1)

                            with m.If(self.cnt != self.arr):
                                m.d.sync += self.cnt.eq(self.cnt + 1)
                            with m.Else():
                                m.d.sync += [
                                    self.dir.eq(~self.dir),
                                    self.cnt.eq(self.cnt - 1)]

                        with m.Case(1): # Counting down

                            with m.If(self.cnt < self.ccr):
                                m.d.sync += self.pins.eq(0)
                            with m.Else():
                                m.d.sync += self.pins.eq(1)

                            with m.If(self.cnt != 0):
                                m.d.sync += self.cnt.eq(self.cnt - 1)
                            with m.Else():
                                m.d.sync += [
                                    self.dir.eq(~self.dir),
                                    self.cnt.eq(self.cnt + 1)]

        return m

# if __name__ == "__main__":
#     from amaranth.sim import * 

#     dut = Timer(Signal(1))

#     def tim_ut(timer):
#         yield timer.en.eq(0)
#         yield timer.ccr.eq(100)
#         yield timer.arr.eq(255)
#         yield timer.alignment.eq(0)

#         for _ in range(20):
#             yield Tick()
#             yield Settle()

        
#         yield timer.en.eq(1)
#         for _ in range(300):
#             yield Tick()
#             yield Settle()

#         yield timer.alignment.eq(1)
#         for _ in range(300):
#             yield Tick()
#             yield Settle()

#         yield timer.alignment.eq(2)
#         for _ in range(600):
#             yield Tick()
#             yield Settle()

#     def proc():
#         yield from tim_ut(dut)

#     sim = Simulator(dut)
#     sim.add_clock(1e-6)
#     sim.add_fast_process(proc)

#     with sim.write_vcd("../sim/timer.vcd", 'w'):
#         sim.run()