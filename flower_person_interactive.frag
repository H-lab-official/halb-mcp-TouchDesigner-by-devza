// Procedural blossoms shaded by the live camera, clipped by the person matte.
uniform vec4 uSettings; // time, density, effect strength, brightness
uniform vec4 uLook; // background brightness, mirror, unused, unused
uniform vec4 uMotion; // amount, rotation speed, sway, bloom
uniform vec4 uReact; // stillness, burst, hue, tracked
out vec4 fragColor;
float hash21(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123); }
vec3 palette(float h) {
    if(h<0.20) return vec3(1.0,0.30,0.48);
    if(h<0.40) return vec3(1.0,0.70,0.23);
    if(h<0.60) return vec3(0.83,0.48,1.0);
    if(h<0.80) return vec3(1.0,0.88,0.71);
    return vec3(1.0,0.49,0.25);
}
vec3 hueShift(vec3 c,float h){vec3 k=vec3(.57735027);float a=h*6.28318;return clamp(c*cos(a)+cross(k,c)*sin(a)+k*dot(k,c)*(1.-cos(a)),0.,1.);}
void main() {
    vec2 uv=vUV.st;
    if(uLook.y>0.5) uv.x=1.0-uv.x;
    vec3 camera=texture(sTD2DInputs[0],uv).rgb;
    float mask=texture(sTD2DInputs[1],uv).a;
    float aspect=uTD2DInfos[0].res.z/uTD2DInfos[0].res.w;
    vec2 gridSize=vec2(aspect,1.0)*uSettings.y;
    vec2 grid=uv*gridSize;
    vec2 cell=floor(grid);
    vec3 flowers=vec3(0.025,0.105,0.055);
    for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) {
        vec2 id=cell+vec2(x,y);
        float h=hash21(id);
        vec2 jitter=vec2(hash21(id+13.2),hash21(id+49.7))-.5;
        float phase=uSettings.x*(.7+h*.8)+h*30.;
        vec2 center=id+.5+jitter*.56;
        center+=uMotion.x*uMotion.z*vec2(sin(phase),cos(phase*.73+h*12.));
        vec2 sampleUV=center/gridSize;
        vec3 shade=texture(sTD2DInputs[0],sampleUV).rgb;
        float lum=dot(shade,vec3(.2126,.7152,.0722));
        float person=texture(sTD2DInputs[1],sampleUV).a;
        vec2 q=grid-center;
        float direction=hash21(id+26.)>.5?1.:-1.;
        float turn=h*6.28318+uMotion.x*(uSettings.x*uMotion.y*(.35+.65*hash21(id+17.))*direction+.22*sin(phase*.6));
        q=mat2(cos(turn),-sin(turn),sin(turn),cos(turn))*q;
        float r=length(q);
        float a=atan(q.y,q.x);
        float petals=5.+floor(hash21(id+9.1)*5.);
        float growth=1.+uMotion.x*uMotion.w*sin(phase*.8);
        growth*=mix(1.,mix(.42,1.45,uReact.x),uReact.w);
        float radius=(.35+.075*cos(a*petals))*growth;
        float blossom=1.-smoothstep(radius-.035,radius+.015,r);
        blossom*=smoothstep(.12,.52,person);
        vec3 petal=hueShift(palette(h),uReact.z)*(.25+.95*sqrt(max(lum,0.)));
        petal*=.76+.24*cos(a*petals);
        petal+=.08*pow(max(0.,1.-r/.45),2.);
        flowers=mix(flowers,petal,blossom);
        float core=(1.-smoothstep(.065*growth,.12*growth,r))*smoothstep(.12,.52,person);
        vec3 gold=mix(vec3(.23,.10,.025),vec3(1.,.78,.18),.5+.5*sin(a*13.+r*180.));
        flowers=mix(flowers,gold*(.4+.6*sqrt(max(lum,0.))),core);
    }
    float matte=smoothstep(.18,.78,mask);
    vec3 personColor=mix(camera,flowers,clamp(uSettings.z,0.,1.));
    vec3 background=texture(sTD2DInputs[2],vUV.st).rgb*uLook.x;
    vec3 outputColor=mix(background,personColor,matte)*uSettings.w;
    fragColor=TDOutputSwizzle(vec4(outputColor,1.));
}
