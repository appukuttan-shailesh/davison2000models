import os
import sys
import sciunit
from neuron import h
from time import sleep
import davison2000unit.capabilities as cap

class mitral_4C(sciunit.Model,
                cap.InjectStepCurrentSoma,
                cap.InjectStepCurrentGlomerulus,
                cap.RecordMembranePotentialSoma):

    def __init__(self, name="4 Compartments", model_dir="."):
        sciunit.Model.__init__(self, name=name)

        base_dir = os.path.abspath(model_dir)
        mod_path = os.path.join(base_dir, "x86_64/.libs/libnrnmech.so.0")
        hoc_path = os.path.join(base_dir, "mosinit.hoc")

        if not os.path.isfile(mod_path):
            os.system("cd " + base_dir + "; nrnivmodl NMODL")
            sleep(2)        # 2 seconds
            while(not os.path.isfile(mod_path)):
                # wait for nmodl compilation
                sleep(1)    # 1 second
        
        # to supress hoc output from Jupyter notebook 
        save_stdout = sys.stdout
        sys.stdout = open('/dev/stdout', 'w')
        h.nrn_load_dll(mod_path)
        h.load_file(hoc_path)
        sys.stdout = save_stdout  #setting output back to before 

    def inject_step_current_soma(self, current):
        h.soma_stim.delay = current['delay']
        h.soma_stim.dur = current['duration']

        # retaining model's internal naming conventions
        h.Ifull = current['amplitude']
        h.injcurrdens = h.Ifull/100072  # note that 100072 um2 is the total membrane area of the full model
        h.soma_stim.amp = h.alphas * h.injcurrdens * h.Atotal

    def inject_step_current_glomerulus(self, current):
        h.glom_stim.delay = current['delay']
        h.glom_stim.dur = current['duration']

        h.glom_stim.amp = current['amplitude']
        # retaining model's internal naming conventions
        h.Ifull = current['amplitude']
        h.injcurrdens = h.Ifull/100072  # note that 100072 um2 is the total membrane area of the full model
        h.glom_stim.amp = h.alphag * h.injcurrdens * h.Atotal

    def remove_stimuli(self):
        h.soma_stim.amp = 0
        h.glom_stim.amp = 0

    def get_membrane_potential_soma(self, tstop):
        # to supress hoc output from Jupyter notebook 
        save_stdout = sys.stdout
        sys.stdout = open('/dev/stdout', 'w')

        t_vec = h.Vector()
        v_vec = h.Vector()
        t_vec.record(h._ref_t)
        v_vec.record(h.soma(0.5)._ref_v)
        h.tstop = tstop
        h.run()

        sys.stdout = save_stdout  #setting output back to before 
        return [t_vec.to_python(), v_vec.to_python()]
