#include "model_interface.hpp"
#define CClass PYSIMLINK::Model

extern "C"{
    void* new_model(void){
        return new CClass;
    }

    void delete_model (void *ptr){
        CClass * ref = reinterpret_cast<CClass *>(ptr);
        ref->~Model();
        delete ptr;
    }

    void call_reset(void *ptr){
        CClass * ref = reinterpret_cast<CClass *>(ptr);
        ref->reset();
    }

    void call_print_params(void *ptr){
        CClass * ref = reinterpret_cast<CClass *>(ptr);
        ref->print_params();
    }

}
