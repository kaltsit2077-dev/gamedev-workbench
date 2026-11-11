using System;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class WorkbenchSmoke
{
    [Serializable] private class Check { public string name; public bool passed; }
    [Serializable] private class Report { public string engine = "unity"; public string engine_version; public bool passed; public Check[] checks; }
    private sealed class Charge
    {
        public int Value { get; private set; }
        public event Action<int> Changed;
        public void Trigger() { Value = Math.Min(5, Value + 1); Changed?.Invoke(Value); }
        public void Reset() { Value = 0; Changed?.Invoke(Value); }
    }
    public static void Run()
    {
        string reportPath = Environment.GetEnvironmentVariable("GDW_EDITOR_REPORT");
        if (string.IsNullOrEmpty(reportPath)) throw new InvalidOperationException("GDW_EDITOR_REPORT is required");
        var result = new Report { engine_version = Application.unityVersion };
        GameObject temporary = null;
        try
        {
            var state = new Charge(); int observed = -1;
            state.Changed += value => observed = value;
            for (int i = 0; i < 20; i++) state.Trigger();
            bool bounded = state.Value == 5 && observed == 5;
            state.Reset(); bool notified = state.Value == 0 && observed == 0;
            temporary = new GameObject("WorkbenchOriginalFixture");
            temporary.transform.position = new Vector3(1, 2, 3);
            bool nativeObject = temporary.transform.position == new Vector3(1, 2, 3);
            UnityEngine.Object.DestroyImmediate(temporary);
            bool cleaned = temporary == null;
            result.checks = new[] {
                new Check { name = "model saturates and notifies", passed = bounded },
                new Check { name = "reset notifies", passed = notified },
                new Check { name = "native object transform", passed = nativeObject },
                new Check { name = "native object cleanup", passed = cleaned }
            };
            result.passed = bounded && notified && nativeObject && cleaned;
        }
        finally
        {
            if (temporary != null) UnityEngine.Object.DestroyImmediate(temporary);
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
            File.WriteAllText(reportPath, JsonUtility.ToJson(result, true));
        }
        Debug.Log(result.passed ? "WORKBENCH_EDITOR: PASS" : "WORKBENCH_EDITOR: FAIL");
        if (!result.passed) throw new InvalidOperationException("Original fixture did not pass");
    }
}
