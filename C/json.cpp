// rapidjson/example/simpledom/simpledom.cpp
#include "3rdpart/rapidjson/document.h"
#include "3rdpart/rapidjson/writer.h"
#include "3rdpart/rapidjson/stringbuffer.h"
#include <iostream>

using namespace rapidjson;

int main()
{
    // 1. 把 JSON 解析至 DOM。
    const char *json = "{\"project\":\"rapidjson\",\"stars\":10}";
    Document d;
    d.Parse(json);
    // 2. 利用 DOM 作出修改。
    Value &s = d["stars"];
    s.SetInt(s.GetInt() + 1);
    // 3. 把 DOM 转换（stringify）成 JSON。
    StringBuffer buffer;
    Writer<StringBuffer> writer(buffer);
    d.Accept(writer);
    // Output {"project":"rapidjson","stars":11}
    std::cout << buffer.GetString() << std::endl;
    return 0;
}
