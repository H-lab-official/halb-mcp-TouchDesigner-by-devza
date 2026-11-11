// Soft silhouette rim, warm bloom, and drifting petal trails over the scene.
uniform vec4 uEdge; // glow amount, particles amount, mirror camera, time
out vec4 fragColor;
void main(){
 vec2 uv=vUV.st; vec2 personUV=uv;
 if(uEdge.z>.5) personUV.x=1.-personUV.x;
 vec3 scene=texture(sTD2DInputs[0],uv).rgb;
 float hard=texture(sTD2DInputs[1],personUV).r;
 float soft=texture(sTD2DInputs[1],personUV).g;
 vec2 px=uTD2DInfos[0].res.xy*2.;
 vec3 smoothed=(scene*2.+texture(sTD2DInputs[0],uv+vec2(px.x,0)).rgb+texture(sTD2DInputs[0],uv-vec2(px.x,0)).rgb+texture(sTD2DInputs[0],uv+vec2(0,px.y)).rgb+texture(sTD2DInputs[0],uv-vec2(0,px.y)).rgb)/6.;
 scene=mix(scene,smoothed,clamp(abs(soft-hard)*2.,0.,.65));
 float halo=soft*(1.-smoothstep(.15,.9,hard))*3.;
 float inner=abs(soft-hard)*.5;
 vec3 tint=mix(vec3(1.,.35,.58),vec3(1.,.76,.28),.5+.5*sin(personUV.y*5.+uEdge.w*.45));
 vec3 glow=tint*(halo+inner)*uEdge.x;
 vec3 particles=texture(sTD2DInputs[2],personUV).rgb*uEdge.y;
 vec3 additions=glow+particles;
 vec3 color=1.-(1.-clamp(scene,0.,1.))*exp(-additions);
 fragColor=TDOutputSwizzle(vec4(color,1.));
}
