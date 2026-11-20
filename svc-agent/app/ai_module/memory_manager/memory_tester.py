from yachalk import chalk
import uuid
from app.ai_module.memory_manager.memory import Memory

class MemoryTester:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = None

    def start_test(self):
        self.memory = Memory(session_id = self.session_id)
        try:
            print(chalk.blue.bold(f"\n[STARTING MEMORY DIAGNOSIS FOR ARBITRARY SESSION ID]\n"))

            print(chalk.blue.bold(f"[ATTEMPTING ARIBITRARY MESSAGE INSERTION...]\n"))
            for index in range(1, 11):
                self.memory.add_message("SYSTEM", f"MESSAGE NO. {index} / 10 : {str(uuid.uuid4())}")
            print(chalk.green.bold(f"[ARIBITRARY MESSAGE INSERTION COMPLETED SUCCESSFULLY]\n"))

            print(chalk.blue.bold(f"[ATTEMPTING FULL HISTORY RETRIEVAL...]\n"))
            full_history = self.memory.get_history()
            for history_entry in full_history:
                print(f"{history_entry}")
            print(chalk.green.bold(f"\n[FULL HISTORY RETRIEVED SUCCESSFULLY]\n"))

            print(chalk.blue.bold(f"[ATTEMPTING PARTIAL HISTORY RETRIEVAL (LAST 5 MESSAGES)...]\n"))
            partial_history = self.memory.get_last_messages()
            for history_entry in partial_history:
                print(f"{history_entry}")
            print(chalk.green.bold(f"\n[PARTIAL HISTORY RETRIEVAL COMPLETED SUCCESFULLY]\n"))

            print(chalk.blue.bold(f"[ATTEMPTING HISTORY CLEARANCE...]\n"))
            self.memory.clear_session()
            print(chalk.blue.bold(f"[CHECKING EMPTINESS...]"))
            if len(self.memory.get_history()) == 0:
                print(chalk.green.bold(f"[THE HISTORY LIST IS EMPTY.]"))
                print(chalk.green.bold(f"\n[HISTORY CLEARANCE COMPLETED SUCCESFULLY]\n"))
            else:
                print(chalk.red.bold(f"[THE HISTORY LIST IS NOT EMPTY.]\n"))

            print(chalk.green.bold(f"[ALL TESTS HAVE BEEN COMPLETED SUCCESSFULLY. ALL MEMORY SYSTEMS ARE OPERATIONAL AND READY.]\n"))

        except Exception as e:
            print(chalk.red.bold(f"AN ERROR HAS BEEN DETECTED DURING THE DIAGNOSIS PROCESS. MORE INFO BELOW:"))
            print(chalk.red.bold(f"CAUSE: {e}"))

