var le=globalThis,de=le.ShadowRoot&&(le.ShadyCSS===void 0||le.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,De=Symbol(),rt=new WeakMap,G=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==De)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(de&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=rt.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&rt.set(t,e))}return e}toString(){return this.cssText}},at=o=>new G(typeof o=="string"?o:o+"",void 0,De),g=(o,...e)=>{let t=o.length===1?o[0]:e.reduce((i,r,a)=>i+(s=>{if(s._$cssResult$===!0)return s.cssText;if(typeof s=="number")return s;throw Error("Value passed to 'css' function must be a 'css' function result: "+s+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[a+1],o[0]);return new G(t,o,De)},st=(o,e)=>{if(de)o.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),r=le.litNonce;r!==void 0&&i.setAttribute("nonce",r),i.textContent=t.cssText,o.appendChild(i)}},Me=de?o=>o:o=>o instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return at(t)})(o):o;var{is:pi,defineProperty:fi,getOwnPropertyDescriptor:vi,getOwnPropertyNames:gi,getOwnPropertySymbols:wi,getPrototypeOf:bi}=Object,he=globalThis,nt=he.trustedTypes,yi=nt?nt.emptyScript:"",Ci=he.reactiveElementPolyfillSupport,J=(o,e)=>o,Z={toAttribute(o,e){switch(e){case Boolean:o=o?yi:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,e){let t=o;switch(e){case Boolean:t=o!==null;break;case Number:t=o===null?null:Number(o);break;case Object:case Array:try{t=JSON.parse(o)}catch{t=null}}return t}},ue=(o,e)=>!pi(o,e),ct={attribute:!0,type:String,converter:Z,reflect:!1,useDefault:!1,hasChanged:ue};Symbol.metadata??=Symbol("metadata"),he.litPropertyMetadata??=new WeakMap;var _=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=ct){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),r=this.getPropertyDescriptor(e,i,t);r!==void 0&&fi(this.prototype,e,r)}}static getPropertyDescriptor(e,t,i){let{get:r,set:a}=vi(this.prototype,e)??{get(){return this[t]},set(s){this[t]=s}};return{get:r,set(s){let n=r?.call(this);a?.call(this,s),this.requestUpdate(e,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??ct}static _$Ei(){if(this.hasOwnProperty(J("elementProperties")))return;let e=bi(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(J("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(J("properties"))){let t=this.properties,i=[...gi(t),...wi(t)];for(let r of i)this.createProperty(r,t[r])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,r]of t)this.elementProperties.set(i,r)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let r=this._$Eu(t,i);r!==void 0&&this._$Eh.set(r,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let r of i)t.unshift(Me(r))}else e!==void 0&&t.push(Me(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return st(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),r=this.constructor._$Eu(e,i);if(r!==void 0&&i.reflect===!0){let a=(i.converter?.toAttribute!==void 0?i.converter:Z).toAttribute(t,i.type);this._$Em=e,a==null?this.removeAttribute(r):this.setAttribute(r,a),this._$Em=null}}_$AK(e,t){let i=this.constructor,r=i._$Eh.get(e);if(r!==void 0&&this._$Em!==r){let a=i.getPropertyOptions(r),s=typeof a.converter=="function"?{fromAttribute:a.converter}:a.converter?.fromAttribute!==void 0?a.converter:Z;this._$Em=r;let n=s.fromAttribute(t,a.type);this[r]=n??this._$Ej?.get(r)??n,this._$Em=null}}requestUpdate(e,t,i,r=!1,a){if(e!==void 0){let s=this.constructor;if(r===!1&&(a=this[e]),i??=s.getPropertyOptions(e),!((i.hasChanged??ue)(a,t)||i.useDefault&&i.reflect&&a===this._$Ej?.get(e)&&!this.hasAttribute(s._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:r,wrapped:a},s){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,s??t??this[e]),a!==!0||s!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),r===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,a]of this._$Ep)this[r]=a;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[r,a]of i){let{wrapped:s}=a,n=this[r];s!==!0||this._$AL.has(r)||n===void 0||this.C(r,void 0,a,n)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};_.elementStyles=[],_.shadowRootOptions={mode:"open"},_[J("elementProperties")]=new Map,_[J("finalized")]=new Map,Ci?.({ReactiveElement:_}),(he.reactiveElementVersions??=[]).push("2.1.2");var Te=globalThis,lt=o=>o,me=Te.trustedTypes,dt=me?me.createPolicy("lit-html",{createHTML:o=>o}):void 0,Pe="$lit$",E=`lit$${Math.random().toFixed(9).slice(2)}$`,Ie="?"+E,xi=`<${Ie}>`,R=document,ee=()=>R.createComment(""),te=o=>o===null||typeof o!="object"&&typeof o!="function",Re=Array.isArray,vt=o=>Re(o)||typeof o?.[Symbol.iterator]=="function",Fe=`[ 	
\f\r]`,Q=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ht=/-->/g,ut=/>/g,P=RegExp(`>|${Fe}(?:([^\\s"'>=/]+)(${Fe}*=${Fe}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),mt=/'/g,pt=/"/g,gt=/^(?:script|style|textarea|title)$/i,Be=o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),h=Be(1),wt=Be(2),bt=Be(3),k=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),ft=new WeakMap,I=R.createTreeWalker(R,129);function yt(o,e){if(!Re(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return dt!==void 0?dt.createHTML(e):e}var Ct=(o,e)=>{let t=o.length-1,i=[],r,a=e===2?"<svg>":e===3?"<math>":"",s=Q;for(let n=0;n<t;n++){let c=o[n],l,v,f=-1,y=0;for(;y<c.length&&(s.lastIndex=y,v=s.exec(c),v!==null);)y=s.lastIndex,s===Q?v[1]==="!--"?s=ht:v[1]!==void 0?s=ut:v[2]!==void 0?(gt.test(v[2])&&(r=RegExp("</"+v[2],"g")),s=P):v[3]!==void 0&&(s=P):s===P?v[0]===">"?(s=r??Q,f=-1):v[1]===void 0?f=-2:(f=s.lastIndex-v[2].length,l=v[1],s=v[3]===void 0?P:v[3]==='"'?pt:mt):s===pt||s===mt?s=P:s===ht||s===ut?s=Q:(s=P,r=void 0);let A=s===P&&o[n+1].startsWith("/>")?" ":"";a+=s===Q?c+xi:f>=0?(i.push(l),c.slice(0,f)+Pe+c.slice(f)+E+A):c+E+(f===-2?n:A)}return[yt(o,a+(o[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},ie=class o{constructor({strings:e,_$litType$:t},i){let r;this.parts=[];let a=0,s=0,n=e.length-1,c=this.parts,[l,v]=Ct(e,t);if(this.el=o.createElement(l,i),I.currentNode=this.el.content,t===2||t===3){let f=this.el.content.firstChild;f.replaceWith(...f.childNodes)}for(;(r=I.nextNode())!==null&&c.length<n;){if(r.nodeType===1){if(r.hasAttributes())for(let f of r.getAttributeNames())if(f.endsWith(Pe)){let y=v[s++],A=r.getAttribute(f).split(E),C=/([.?@])?(.*)/.exec(y);c.push({type:1,index:a,name:C[2],strings:A,ctor:C[1]==="."?fe:C[1]==="?"?ve:C[1]==="@"?ge:O}),r.removeAttribute(f)}else f.startsWith(E)&&(c.push({type:6,index:a}),r.removeAttribute(f));if(gt.test(r.tagName)){let f=r.textContent.split(E),y=f.length-1;if(y>0){r.textContent=me?me.emptyScript:"";for(let A=0;A<y;A++)r.append(f[A],ee()),I.nextNode(),c.push({type:2,index:++a});r.append(f[y],ee())}}}else if(r.nodeType===8)if(r.data===Ie)c.push({type:2,index:a});else{let f=-1;for(;(f=r.data.indexOf(E,f+1))!==-1;)c.push({type:7,index:a}),f+=E.length-1}a++}}static createElement(e,t){let i=R.createElement("template");return i.innerHTML=e,i}};function B(o,e,t=o,i){if(e===k)return e;let r=i!==void 0?t._$Co?.[i]:t._$Cl,a=te(e)?void 0:e._$litDirective$;return r?.constructor!==a&&(r?._$AO?.(!1),a===void 0?r=void 0:(r=new a(o),r._$AT(o,t,i)),i!==void 0?(t._$Co??=[])[i]=r:t._$Cl=r),r!==void 0&&(e=B(o,r._$AS(o,e.values),r,i)),e}var pe=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,r=(e?.creationScope??R).importNode(t,!0);I.currentNode=r;let a=I.nextNode(),s=0,n=0,c=i[0];for(;c!==void 0;){if(s===c.index){let l;c.type===2?l=new N(a,a.nextSibling,this,e):c.type===1?l=new c.ctor(a,c.name,c.strings,this,e):c.type===6&&(l=new we(a,this,e)),this._$AV.push(l),c=i[++n]}s!==c?.index&&(a=I.nextNode(),s++)}return I.currentNode=R,r}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},N=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,r){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=B(this,e,t),te(e)?e===u||e==null||e===""?(this._$AH!==u&&this._$AR(),this._$AH=u):e!==this._$AH&&e!==k&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):vt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==u&&te(this._$AH)?this._$AA.nextSibling.data=e:this.T(R.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,r=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=ie.createElement(yt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(t);else{let a=new pe(r,this),s=a.u(this.options);a.p(t),this.T(s),this._$AH=a}}_$AC(e){let t=ft.get(e.strings);return t===void 0&&ft.set(e.strings,t=new ie(e)),t}k(e){Re(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,r=0;for(let a of e)r===t.length?t.push(i=new o(this.O(ee()),this.O(ee()),this,this.options)):i=t[r],i._$AI(a),r++;r<t.length&&(this._$AR(i&&i._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=lt(e).nextSibling;lt(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},O=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,r,a){this.type=1,this._$AH=u,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=a,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=u}_$AI(e,t=this,i,r){let a=this.strings,s=!1;if(a===void 0)e=B(this,e,t,0),s=!te(e)||e!==this._$AH&&e!==k,s&&(this._$AH=e);else{let n=e,c,l;for(e=a[0],c=0;c<a.length-1;c++)l=B(this,n[i+c],t,c),l===k&&(l=this._$AH[c]),s||=!te(l)||l!==this._$AH[c],l===u?e=u:e!==u&&(e+=(l??"")+a[c+1]),this._$AH[c]=l}s&&!r&&this.j(e)}j(e){e===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},fe=class extends O{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===u?void 0:e}},ve=class extends O{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==u)}},ge=class extends O{constructor(e,t,i,r,a){super(e,t,i,r,a),this.type=5}_$AI(e,t=this){if((e=B(this,e,t,0)??u)===k)return;let i=this._$AH,r=e===u&&i!==u||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,a=e!==u&&(i===u||r);r&&this.element.removeEventListener(this.name,this,i),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},we=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){B(this,e)}},xt={M:Pe,P:E,A:Ie,C:1,L:Ct,R:pe,D:vt,V:B,I:N,H:O,N:ve,U:ge,B:fe,F:we},Li=Te.litHtmlPolyfillSupport;Li?.(ie,N),(Te.litHtmlVersions??=[]).push("3.3.3");var Lt=(o,e,t)=>{let i=t?.renderBefore??e,r=i._$litPart$;if(r===void 0){let a=t?.renderBefore??null;i._$litPart$=r=new N(e.insertBefore(ee(),a),a,void 0,t??{})}return r._$AI(o),r};var Oe=globalThis,x=class extends _{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Lt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return k}};x._$litElement$=!0,x.finalized=!0,Oe.litElementHydrateSupport?.({LitElement:x});var $i=Oe.litElementPolyfillSupport;$i?.({LitElement:x});(Oe.litElementVersions??=[]).push("4.2.2");var $t={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},be=o=>(...e)=>({_$litDirective$:o,values:e}),H=class{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}};var{I:zo}=xt;var St=(o,e)=>e===void 0?o?._$litType$!==void 0:o?._$litType$===e;var Si={},zt=(o,e=Si)=>o._$AH=e;var At=be(class extends H{constructor(){super(...arguments),this.key=u}render(o,e){return this.key=o,e}update(o,[e,t]){return e!==this.key&&(zt(o),this.key=e),t}});var ye=class{constructor(e){this.onStatus=e;this.socket=null;this.connected=!1;this.nextId=0;this.pending=new Map}connect(e){this.disconnect(),this.onStatus("connecting"),this.openSocket(e)}openSocket(e){let t=new WebSocket(`ws://${location.host}/api/websocket`);this.socket=t,t.onopen=()=>{this.socket===t&&t.send(JSON.stringify({token:e}))},t.onmessage=i=>{if(this.socket!==t)return;let r=JSON.parse(i.data);if(r.type==="ready"){this.connected=!0,this.onStatus("connected");return}if(r.id===void 0)return;let a=this.pending.get(r.id);if(a){if(r.type==="discovery/device"){r.device&&a.onDiscovered?.(r.device);return}clearTimeout(a.timer),this.pending.delete(r.id),r.error?a.reject(new Error(r.error.message)):a.resolve(r.result)}},t.onclose=i=>{if(this.socket===t){if(this.disconnect(),i.code===1008){this.onStatus("denied");return}this.onStatus("reconnecting"),this.reconnectTimer=setTimeout(()=>this.openSocket(e),2e3)}}}disconnect(){clearTimeout(this.reconnectTimer);let e=this.socket;this.socket=null,this.connected=!1,e?.close();for(let t of this.pending.values())clearTimeout(t.timer),t.reject(new Error("Connection lost. Try again once reconnected."));this.pending.clear()}callWS(e,t,i){let r=this.socket;if(r?.readyState!==WebSocket.OPEN||!this.connected)return Promise.reject(new Error("Not connected."));let a=++this.nextId;return new Promise((s,n)=>{let c=setTimeout(()=>{this.pending.delete(a),n(new Error("Request timed out."))},65e3);this.pending.set(a,{resolve:l=>s(l),reject:n,timer:c,onDiscovered:i}),r.send(JSON.stringify({id:a,type:e,...t}))})}};var _t=o=>o.callWS("devices/list",{}),Et=(o,e)=>o.callWS("devices/discover",{stream:!0},e),kt=(o,e)=>o.callWS("devices/save",e),Dt=(o,e)=>o.callWS("device/settings",{device:e}),Mt=(o,e,t)=>o.callWS("device/configure",{device:e,...t}),Ft=(o,e)=>o.callWS("device/health",{device:e}),Tt=(o,e)=>o.callWS("device/apis",{device:e}),Pt=(o,e)=>o.callWS("device/interfaces",{device:e}),It=(o,e,t)=>o.callWS("device/read",{device:e,name:t});function oe(o){return o.alias.trim()||o.discovery?.name.trim()||o.model.trim()||o.serial}var zi=g`
  :root {
    color-scheme: light dark;
    --axis-color-background: light-dark(#f5f7fa, #11151c);
    --axis-color-surface: light-dark(#ffffff, #1d2430);
    --axis-color-surface-muted: light-dark(#eaf0f6, #293342);
    --axis-color-text: light-dark(#202630, #edf2f8);
    --axis-color-border: light-dark(#bac5d2, #58677b);
    --axis-color-primary: light-dark(#005e9e, #8bcbff);
    --axis-color-on-primary: light-dark(#ffffff, #072c48);
    --axis-color-danger: light-dark(#a00000, #ffb4ab);
    --axis-color-success: light-dark(#006b3c, #85d9a8);
    --axis-color-warning: light-dark(#805000, #ffd08a);
    --axis-font-family: system-ui, sans-serif;
    --axis-font-size: 1rem;
    --axis-font-weight-medium: 600;
    --axis-line-height: 1.5;
    --axis-space-1: 0.25rem;
    --axis-space-2: 0.5rem;
    --axis-space-3: 0.75rem;
    --axis-space-4: 1rem;
    --axis-space-6: 1.5rem;
    --axis-radius-control: 0.5rem;
    --axis-radius-card: 0.75rem;
    --axis-border-width: 1px;
    --axis-control-height: 2.75rem;
    --axis-content-width: 62.5rem;
    --axis-focus-ring: 2px solid var(--axis-color-primary);

    --wa-font-family-body: var(--axis-font-family);
    --wa-font-size-m: var(--axis-font-size);
    --wa-color-text-normal: var(--axis-color-text);
    --wa-color-surface-default: var(--axis-color-surface);
    --wa-color-surface-border: var(--axis-color-border);
    --wa-color-neutral-fill-loud: var(--axis-color-text);
    --wa-color-neutral-on-loud: var(--axis-color-surface);
    --wa-color-neutral-fill-normal: var(--axis-color-surface-muted);
    --wa-color-neutral-on-normal: var(--axis-color-text);
    --wa-color-neutral-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-neutral-on-quiet: var(--axis-color-text);
    --wa-color-neutral-border-normal: var(--axis-color-border);
    --wa-color-neutral-border-quiet: var(--axis-color-border);
    --wa-color-neutral-border-loud: var(--axis-color-border);
    --wa-color-brand-fill-loud: var(--axis-color-primary);
    --wa-color-brand-on-loud: var(--axis-color-on-primary);
    --wa-color-brand-fill-normal: var(--axis-color-surface-muted);
    --wa-color-brand-on-normal: var(--axis-color-primary);
    --wa-color-brand-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-brand-on-quiet: var(--axis-color-primary);
    --wa-color-brand-border-normal: var(--axis-color-primary);
    --wa-color-brand-border-quiet: var(--axis-color-border);
    --wa-color-brand-border-loud: var(--axis-color-primary);
    --wa-color-success-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-success-on-quiet: var(--axis-color-success);
    --wa-color-success-border-loud: var(--axis-color-success);
    --wa-color-danger-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-danger-on-quiet: var(--axis-color-danger);
    --wa-color-danger-border-loud: var(--axis-color-danger);
    --wa-color-mix-hover: var(--axis-color-border) 20%;
    --wa-color-mix-active: var(--axis-color-border) 30%;
    --wa-focus-ring: var(--axis-focus-ring);
    --wa-focus-ring-offset: var(--axis-space-1);

    font-family: var(--axis-font-family);
    font-size: var(--axis-font-size);
    line-height: var(--axis-line-height);
    color: var(--axis-color-text);
    background: var(--axis-color-background);
  }

  body {
    margin: 0;
  }
`,Rt=document.createElement("style");Rt.textContent=zi.cssText;document.head.append(Rt);var U=g`
  :host {
    display: block;
    min-inline-size: 0;
  }
  h2 {
    margin-block: 0 var(--axis-space-4);
    overflow-wrap: anywhere;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--axis-space-2);
    margin-block-start: var(--axis-space-2);
  }
  .warning {
    color: var(--axis-color-warning);
    font-weight: var(--axis-font-weight-medium);
  }
  dl {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    gap: var(--axis-space-2) var(--axis-space-4);
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  pre {
    overflow: auto;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: var(--axis-color-surface-muted);
    padding: var(--axis-space-4);
    border-radius: var(--axis-radius-control);
  }
`;var M=o=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(o,e)}):customElements.define(o,e)};var Ai={attribute:!0,type:String,converter:Z,reflect:!1,hasChanged:ue},_i=(o=Ai,e,t)=>{let{kind:i,metadata:r}=t,a=globalThis.litPropertyMetadata.get(r);if(a===void 0&&globalThis.litPropertyMetadata.set(r,a=new Map),i==="setter"&&((o=Object.create(o)).wrapped=!0),a.set(t.name,o),i==="accessor"){let{name:s}=t;return{set(n){let c=e.get.call(this);e.set.call(this,n),this.requestUpdate(s,c,o,!0,n)},init(n){return n!==void 0&&this.C(s,void 0,o,n),n}}}if(i==="setter"){let{name:s}=t;return function(n){let c=this[s];e.call(this,n),this.requestUpdate(s,c,o,!0,n)}}throw Error("Unsupported decorator location: "+i)};function d(o){return(e,t)=>typeof t=="object"?_i(o,e,t):((i,r,a)=>{let s=r.hasOwnProperty(a);return r.constructor.createProperty(a,i),s?Object.getOwnPropertyDescriptor(r,a):void 0})(o,e,t)}function re(o){return d({...o,state:!0,attribute:!1})}var V=(o,e,t)=>(t.configurable=!0,t.enumerable=!0,Reflect.decorate&&typeof e!="object"&&Object.defineProperty(o,e,t),t);function Ve(o,e){return(t,i,r)=>{let a=s=>s.renderRoot?.querySelector(o)??null;if(e){let{get:s,set:n}=typeof i=="object"?t:r??(()=>{let c=Symbol();return{get(){return this[c]},set(l){this[c]=l}}})();return V(t,i,{get(){let c=s.call(this);return c===void 0&&(c=a(this),(c!==null||this.hasUpdated)&&n.call(this,c)),c}})}return V(t,i,{get(){return a(this)}})}}var ae=be(class extends H{constructor(o){if(super(o),o.type!==$t.ATTRIBUTE||o.name!=="class"||o.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(o){return" "+Object.keys(o).filter(e=>o[e]).join(" ")+" "}update(o,[e]){if(this.st===void 0){this.st=new Set,o.strings!==void 0&&(this.nt=new Set(o.strings.join(" ").split(/\s/).filter(i=>i!=="")));for(let i in e)e[i]&&!this.nt?.has(i)&&this.st.add(i);return this.render(e)}let t=o.element.classList;for(let i of this.st)i in e||(t.remove(i),this.st.delete(i));for(let i in e){let r=!!e[i];r===this.st.has(i)||this.nt?.has(i)||(r?(t.add(i),this.st.add(i)):(t.remove(i),this.st.delete(i)))}return k}});var S=o=>o??u;var Ot=Symbol.for(""),Ei=o=>{if(o?.r===Ot)return o?._$litStatic$};var qe=(o,...e)=>({_$litStatic$:e.reduce((t,i,r)=>t+(a=>{if(a._$litStatic$!==void 0)return a._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${a}. Use 'unsafeStatic' to pass non-literal values, but
            take care to ensure page security.`)})(i)+o[r+1],o[0]),r:Ot}),Bt=new Map,Ne=o=>(e,...t)=>{let i=t.length,r,a,s=[],n=[],c,l=0,v=!1;for(;l<i;){for(c=e[l];l<i&&(a=t[l],(r=Ei(a))!==void 0);)c+=r+e[++l],v=!0;l!==i&&n.push(a),s.push(c),l++}if(l===i&&s.push(e[i]),v){let f=s.join("$$lit$$");(e=Bt.get(f))===void 0&&(s.raw=s,Bt.set(f,e=s)),t=n}return o(e,...t)},Ce=Ne(h),$r=Ne(wt),Sr=Ne(bt);var j=class extends Event{constructor(){super("wa-invalid",{bubbles:!0,cancelable:!1,composed:!0})}};var Vt={small:"s",medium:"m",large:"l"};var qt=new Set;function Nt(o,e){e in Vt&&!qt.has(`${o}:${e}`)&&(qt.add(`${o}:${e}`),console.warn(`[${o}] size="${e}" is deprecated. Use size="${Vt[e]}" instead. The long-form value will be removed in the next major version.`))}var W=class{constructor(e,...t){this.slotNames=[],this.handleSlotChange=i=>{let r=i.target;(this.slotNames.includes("[default]")&&!r.name||r.name&&this.slotNames.includes(r.name))&&this.host.requestUpdate()},(this.host=e).addController(this),this.slotNames=t}hasDefaultSlot(){return this.host.childNodes?[...this.host.childNodes].some(e=>{if(e.nodeType===Node.TEXT_NODE&&e.textContent.trim()!=="")return!0;if(e.nodeType===Node.ELEMENT_NODE){let t=e;if(t.tagName.toLowerCase()==="wa-visually-hidden")return!1;if(!t.hasAttribute("slot"))return!0}return!1}):!1}hasNamedSlot(e){return this.host.querySelector?.(`:scope > [slot="${e}"]`)!==null}test(e,t){return t&&this.host.didSSR&&!this.host.hasUpdated?!!this.host[t]:e==="[default]"?this.hasDefaultSlot():this.hasNamedSlot(e)}hostConnected(){let e=this.host.shadowRoot;e&&"addEventListener"in e&&e.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){let e=this.host.shadowRoot;e&&"removeEventListener"in e&&e.removeEventListener("slotchange",this.handleSlotChange)}};var Ht=()=>({checkValidity(o){let e=o.input,t={message:"",isValid:!0,invalidKeys:[]};if(!e)return t;let i=!0;if("checkValidity"in e&&(i=e.checkValidity()),i)return t;if(t.isValid=!1,"validationMessage"in e&&(t.message=e.validationMessage),!("validity"in e))return t.invalidKeys.push("customError"),t;for(let r in e.validity){if(r==="valid")continue;let a=r;e.validity[a]&&t.invalidKeys.push(a)}return t}});function F(o,e){let t={waitUntilFirstUpdate:!1,...e};return(i,r)=>{let{update:a}=i,s=Array.isArray(o)?o:[o];i.update=function(n){s.forEach(c=>{let l=c;if(n.has(l)){let v=n.get(l),f=this[l];v!==f&&(!t.waitUntilFirstUpdate||this.hasUpdated)&&this[r](v,f)}}),a.call(this,n)}}}var Ut=()=>({observedAttributes:["custom-error"],checkValidity(o){let e={message:"",isValid:!0,invalidKeys:[]};return o.customError&&(e.message=o.customError,e.isValid=!1,e.invalidKeys=["customError"]),e}});var jt=g`:host {
  box-sizing: border-box;
}
:host *,
:host *::before,
:host *::after {
  box-sizing: inherit;
}
[hidden],
:host([hidden]) {
  display: none !important;
}
`;var xe=class extends Set{constructor(e,t=null){super(),this._existing=null,this._el=e,this._existing=t}add(e){super.add(e);let t=this._existing;if(t)try{t.add(e)}catch{t.add(`--${e}`)}else this._el.setAttribute(`state-${e}`,"");return this}delete(e){super.delete(e);let t=this._existing;return t?(t.delete(e),t.delete(`--${e}`)):this._el.removeAttribute(`state-${e}`),!0}has(e){return super.has(e)}clear(){for(let e of this)this.delete(e)}};if(typeof CSSStyleSheet<"u"){let o=CSSStyleSheet.prototype.replaceSync;Object.defineProperty(CSSStyleSheet.prototype,"replaceSync",{value:function(e){e=e.replace(/:state\(([^)]+)\)/g,":is(:state($1), :--$1, [state-$1])"),o.call(this,e)}})}var ki=Object.defineProperty,Di=Object.getOwnPropertyDescriptor,Xt=o=>{throw TypeError(o)},He=(o,e,t,i)=>{for(var r=i>1?void 0:i?Di(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&ki(e,t,r),r},Yt=(o,e,t)=>e.has(o)||Xt("Cannot "+t),Mi=(o,e,t)=>(Yt(o,e,"read from private field"),t?t.call(o):e.get(o)),Fi=(o,e,t)=>e.has(o)?Xt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(o):e.set(o,t),Ti=(o,e,t,i)=>(Yt(o,e,"write to private field"),i?i.call(o,t):e.set(o,t),t),Pi=/;\s+$/;function Ii(o){return o.replace(/[A-Z]/g,e=>`-${e.toLowerCase()}`)}function Wt(o){let{property:e,value:t,element:i}=o;if(t){let r=i.getAttribute("style")||"";r&&(r.match(Pi)||(r+=";"),r+=" ");let a=`${e}: ${t}`;return r.includes(a)?void 0:`${r}${a};`}return null}var Le,$=class extends x{constructor(){super(),Fi(this,Le,!1),this.initialReflectedProperties=new Map,this.didSSR=!!this.shadowRoot,this.customStates={set:(t,i)=>{if(this.internals?.states)try{i?this.internals.states.add(t):this.internals.states.delete(t)}catch(r){if(String(r).includes("must start with '--'"))console.error("Your browser implements an outdated version of CustomStateSet. Consider using a polyfill");else throw r}},has:t=>{if(!this.internals?.states)return!1;try{return this.internals.states.has(t)}catch{return!1}}};try{this.internals=this.attachInternals()}catch{console.error("Element internals are not supported in your browser. Consider using a polyfill")}this.customStates.set("wa-defined",!0);let e=this.constructor;for(let[t,i]of e.elementProperties)i.default==="inherit"&&i.initial!==void 0&&typeof t=="string"&&this.customStates.set(`initial-${t}-${i.initial}`,!0)}static get styles(){let e=Array.isArray(this.css)?this.css:this.css?[this.css]:[];return[jt,...e]}attachInternals(){let e=super.attachInternals();return Object.defineProperty(e,"states",{value:new xe(this,e.states)}),e}connectedCallback(){super.connectedCallback(),this.didSSR||this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `)),this.didSSR&&this.updateComplete.then(()=>{this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `))})}attributeChangedCallback(e,t,i){Mi(this,Le)||(this.constructor.elementProperties.forEach((r,a)=>{r.reflect&&this[a]!=null&&this.initialReflectedProperties.set(a,this[a])}),Ti(this,Le,!0)),super.attributeChangedCallback(e,t,i)}willUpdate(e){super.willUpdate(e),this.initialReflectedProperties.forEach((t,i)=>{e.has(i)&&this[i]==null&&(this[i]=t)})}firstUpdated(e){super.firstUpdated(e),this.didSSR&&this.shadowRoot?.querySelectorAll("slot").forEach(t=>{t.dispatchEvent(new Event("slotchange",{bubbles:!0,composed:!1,cancelable:!1}))})}update(e){try{super.update(e)}catch(t){if(this.didSSR&&!this.hasUpdated){let i=new Event("lit-hydration-error",{bubbles:!0,composed:!0,cancelable:!1});i.error=t,this.dispatchEvent(i)}throw t}}setStyle(e,t){if(!this.style){let i=Wt({property:Ii(e),value:t,element:this});i&&this.setAttribute("style",i);return}this.style[e]=t}setStyleProperty(e,t){if(!this.style){let i=Wt({property:e,value:t,element:this});i&&this.setAttribute("style",i);return}this.style.setProperty(e,t)}relayNativeEvent(e,t){e.stopImmediatePropagation(),this.dispatchEvent(new e.constructor(e.type,{...e,...t}))}};Le=new WeakMap;He([d()],$.prototype,"dir",2);He([d()],$.prototype,"lang",2);He([d({type:Boolean,reflect:!0,attribute:"did-ssr"})],$.prototype,"didSSR",2);var Ri=Object.defineProperty,Bi=Object.getOwnPropertyDescriptor,X=(o,e,t,i)=>{for(var r=i>1?void 0:i?Bi(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&Ri(e,t,r),r},z=class extends ${constructor(){super(),this.name=null,this.disabled=!1,this.required=!1,this.assumeInteractionOn=["input"],this.validators=[],this.valueHasChanged=!1,this.hasInteracted=!1,this.customError=null,this.emittedEvents=[],this.emitInvalid=e=>{e.target===this&&(this.hasInteracted=!0,this.dispatchEvent(new j))},this.handleInteraction=e=>{let t=this.emittedEvents;t.includes(e.type)||t.push(e.type),t.length===this.assumeInteractionOn?.length&&(this.hasInteracted=!0)},"addEventListener"in this&&this.addEventListener("invalid",this.emitInvalid)}static get validators(){return[Ut()]}static get observedAttributes(){let e=new Set(super.observedAttributes||[]);for(let t of this.validators)if(t.observedAttributes)for(let i of t.observedAttributes)e.add(i);return[...e]}connectedCallback(){super.connectedCallback(),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.updateValidity()}):this.updateValidity(),this.assumeInteractionOn.forEach(e=>{this.addEventListener?.(e,this.handleInteraction)})}firstUpdated(...e){super.firstUpdated(...e),this.updateValidity()}willUpdate(e){if(!!1&&e.has("customError")&&(this.customError||(this.customError=null),this.setCustomValidity(this.customError||"")),e.has("value")||e.has("disabled")||e.has("defaultValue")){let t=this.value;this.updateFormValue(t)}e.has("disabled")&&(this.customStates.set("disabled",this.disabled),(this.hasAttribute("disabled")||!!1&&!this.matches(":disabled"))&&this.toggleAttribute("disabled",this.disabled)),super.willUpdate(e),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>this.updateValidity()):this.updateValidity()}updateFormValue(e){if(Array.isArray(e)){if(this.name){let t=new FormData;for(let i of e)t.append(this.name,i);this.setValue(t,t)}}else this.setValue(e,e)}get labels(){return this.internals.labels}getForm(){return this.internals.form}set form(e){e?this.setAttribute("form",e):this.removeAttribute("form")}get form(){return this.internals.form}get validity(){return this.internals.validity}get willValidate(){return this.internals.willValidate}get validationMessage(){return this.internals.validationMessage}checkValidity(){return this.updateValidity(),this.internals.checkValidity()}reportValidity(){return this.updateValidity(),this.hasInteracted=!0,this.internals.reportValidity()}get validationTarget(){return this.input||void 0}setValidity(...e){let t=e[0],i=e[1],r=e[2];r||(r=this.validationTarget),this.internals.setValidity(t,i,r||void 0),this.requestUpdate("validity"),this.setCustomStates()}setCustomStates(){let e=!!this.required,t=this.internals.validity.valid,i=this.hasInteracted;this.customStates.set("required",e),this.customStates.set("optional",!e),this.customStates.set("invalid",!t),this.customStates.set("valid",t),this.customStates.set("user-invalid",!t&&i),this.customStates.set("user-valid",t&&i)}setCustomValidity(e){if(!e){this.customError=null,this.setValidity({});return}this.customError=e,this.setValidity({customError:!0},e,this.validationTarget)}formResetCallback(){this.resetValidity(),this.hasInteracted=!1,this.valueHasChanged=!1,this.emittedEvents=[],this.updateValidity()}formDisabledCallback(e){this.disabled=e,this.updateValidity()}formStateRestoreCallback(e,t){this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.value=e,t==="restore"&&this.resetValidity(),this.updateValidity()}):(this.value=e,t==="restore"&&this.resetValidity(),this.updateValidity())}setValue(...e){let[t,i]=e;this.internals.setFormValue(t,i)}get allValidators(){let e=this.constructor.validators||[],t=this.validators||[];return[...e,...t]}resetValidity(){this.setCustomValidity(""),this.setValidity({})}updateValidity(){if(this.disabled||this.hasAttribute("disabled")||!this.willValidate){this.resetValidity();return}let e=this.allValidators;if(!e?.length)return;let t={customError:!!this.customError},i=this.validationTarget||this.input||void 0,r="";for(let a of e){let{isValid:s,message:n,invalidKeys:c}=a.checkValidity(this);s||(r||(r=n),c?.length>=0&&c.forEach(l=>t[l]=!0))}r||(r=this.validationMessage),this.setValidity(t,r,i)}};z.formAssociated=!0;X([d({reflect:!0})],z.prototype,"name",2);X([d({type:Boolean})],z.prototype,"disabled",2);X([d({state:!0,attribute:!1})],z.prototype,"valueHasChanged",2);X([d({state:!0,attribute:!1})],z.prototype,"hasInteracted",2);X([d({attribute:"custom-error",reflect:!0})],z.prototype,"customError",2);X([d({attribute:!1,state:!0,type:Object})],z.prototype,"validity",1);var $e=g`:host([size="xs"]) {
  font-size: var(--wa-font-size-xs);
}
:host([size="s"]),
:host([size="small"]) {
  font-size: var(--wa-font-size-s);
}
:host([size="m"]),
:host([size="medium"]) {
  font-size: var(--wa-font-size-m);
}
:host([size="l"]),
:host([size="large"]) {
  font-size: var(--wa-font-size-l);
}
:host([size="xl"]) {
  font-size: var(--wa-font-size-xl);
}
`;var Kt=g`:where(:root),
.wa-neutral,
:host([variant="neutral"]) {
  --wa-color-fill-loud: var(--wa-color-neutral-fill-loud);
  --wa-color-fill-normal: var(--wa-color-neutral-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-neutral-fill-quiet);
  --wa-color-border-loud: var(--wa-color-neutral-border-loud);
  --wa-color-border-normal: var(--wa-color-neutral-border-normal);
  --wa-color-border-quiet: var(--wa-color-neutral-border-quiet);
  --wa-color-on-loud: var(--wa-color-neutral-on-loud);
  --wa-color-on-normal: var(--wa-color-neutral-on-normal);
  --wa-color-on-quiet: var(--wa-color-neutral-on-quiet);
}
.wa-brand,
:host([variant="brand"]) {
  --wa-color-fill-loud: var(--wa-color-brand-fill-loud);
  --wa-color-fill-normal: var(--wa-color-brand-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-brand-fill-quiet);
  --wa-color-border-loud: var(--wa-color-brand-border-loud);
  --wa-color-border-normal: var(--wa-color-brand-border-normal);
  --wa-color-border-quiet: var(--wa-color-brand-border-quiet);
  --wa-color-on-loud: var(--wa-color-brand-on-loud);
  --wa-color-on-normal: var(--wa-color-brand-on-normal);
  --wa-color-on-quiet: var(--wa-color-brand-on-quiet);
}
.wa-success,
:host([variant="success"]) {
  --wa-color-fill-loud: var(--wa-color-success-fill-loud);
  --wa-color-fill-normal: var(--wa-color-success-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-success-fill-quiet);
  --wa-color-border-loud: var(--wa-color-success-border-loud);
  --wa-color-border-normal: var(--wa-color-success-border-normal);
  --wa-color-border-quiet: var(--wa-color-success-border-quiet);
  --wa-color-on-loud: var(--wa-color-success-on-loud);
  --wa-color-on-normal: var(--wa-color-success-on-normal);
  --wa-color-on-quiet: var(--wa-color-success-on-quiet);
}
.wa-warning,
:host([variant="warning"]) {
  --wa-color-fill-loud: var(--wa-color-warning-fill-loud);
  --wa-color-fill-normal: var(--wa-color-warning-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-warning-fill-quiet);
  --wa-color-border-loud: var(--wa-color-warning-border-loud);
  --wa-color-border-normal: var(--wa-color-warning-border-normal);
  --wa-color-border-quiet: var(--wa-color-warning-border-quiet);
  --wa-color-on-loud: var(--wa-color-warning-on-loud);
  --wa-color-on-normal: var(--wa-color-warning-on-normal);
  --wa-color-on-quiet: var(--wa-color-warning-on-quiet);
}
.wa-danger,
:host([variant="danger"]) {
  --wa-color-fill-loud: var(--wa-color-danger-fill-loud);
  --wa-color-fill-normal: var(--wa-color-danger-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-danger-fill-quiet);
  --wa-color-border-loud: var(--wa-color-danger-border-loud);
  --wa-color-border-normal: var(--wa-color-danger-border-normal);
  --wa-color-border-quiet: var(--wa-color-danger-border-quiet);
  --wa-color-on-loud: var(--wa-color-danger-on-loud);
  --wa-color-on-normal: var(--wa-color-danger-on-normal);
  --wa-color-on-quiet: var(--wa-color-danger-on-quiet);
}
`;var Ue=new Set,Y=new Map,D,je="ltr",We="en",Gt=typeof MutationObserver<"u"&&typeof document<"u"&&typeof document.documentElement<"u";if(Gt){let o=new MutationObserver(Jt);je=document.documentElement.dir||"ltr",We=document.documentElement.lang||navigator.language,o.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]})}function ne(...o){o.map(e=>{let t=e.$code.toLowerCase();Y.has(t)?Y.set(t,Object.assign(Object.assign({},Y.get(t)),e)):Y.set(t,e),D||(D=e)}),Jt()}function Jt(){Gt&&(je=document.documentElement.dir||"ltr",We=document.documentElement.lang||navigator.language),[...Ue.keys()].map(o=>{typeof o.requestUpdate=="function"&&o.requestUpdate()})}var Se=class{constructor(e){this.host=e,this.host.addController(this)}hostConnected(){Ue.add(this.host)}hostDisconnected(){Ue.delete(this.host)}dir(){return`${this.host.dir||je}`.toLowerCase()}lang(){let e=`${this.host.lang||We}`.toLowerCase().replace(/_/g,"-");try{return new Intl.Locale(e),e}catch{return D?D.$code.toLowerCase():"en"}}getTranslationData(e){var t,i;let r;try{r=new Intl.Locale(e.replace(/_/g,"-"))}catch{return{locale:void 0,language:"",region:"",primary:void 0,secondary:void 0}}let a=r.language.toLowerCase(),s=(i=(t=r.region)===null||t===void 0?void 0:t.toLowerCase())!==null&&i!==void 0?i:"",n=Y.get(`${a}-${s}`),c=Y.get(a);return{locale:r,language:a,region:s,primary:n,secondary:c}}exists(e,t){var i;let{primary:r,secondary:a}=this.getTranslationData((i=t.lang)!==null&&i!==void 0?i:this.lang());return t=Object.assign({includeFallback:!1},t),!!(r&&r[e]||a&&a[e]||t.includeFallback&&D&&D[e])}term(e,...t){let{primary:i,secondary:r}=this.getTranslationData(this.lang()),a;if(i&&i[e])a=i[e];else if(r&&r[e])a=r[e];else if(D&&D[e])a=D[e];else return console.error(`No translation found for: ${String(e)}`),String(e);return typeof a=="function"?a(...t):a}date(e,t){return e=new Date(e),new Intl.DateTimeFormat(this.lang(),t).format(e)}number(e,t){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(this.lang(),t).format(e)}relativeTime(e,t,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(e,t)}};var Zt={$code:"en",$name:"English",$dir:"ltr",allTagsRemoved:"All tags removed",am:"AM",autosizeColumn:"Autosize column",captions:"Captions",carousel:"Carousel",chooseDate:"Choose date",chooseDecade:"Choose decade",chooseMonth:"Choose month",chooseTime:"Choose time",chooseYear:"Choose year",clearEntry:"Clear entry",clearFilter:"Clear filter",clearSort:"Clear sort",close:"Close",closeCalendar:"Close calendar",closeTimeInput:"Close time picker",collapseRow:"Collapse row",columnMenu:"Column options",columnMovedToPosition:(o,e,t)=>`${o} moved to position ${e} of ${t}`,columns:"Columns",compactPageXOfY:(o,e)=>`${o} of ${e}`,completed:"Completed",copied:"Copied",copy:"Copy",createOption:o=>`Create "${o}"`,currentlyPlaying:"currently playing",currentValue:"Current value",date:"Date",datePickerKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the calendar.",day:"Day",dayPeriod:"AM/PM",decrement:"Decrement",deselectAllRows:"Deselect all rows",disabled:"Disabled",dropFileHere:"Drop file here or click to browse",dropFilesHere:"Drop files here or click to browse",empty:"Empty",endDate:"End date",enterFullscreen:"Enter fullscreen",error:"Error",exitFullscreen:"Exit fullscreen",expandRow:"Expand row",filterByColumn:o=>`Filter by ${o}`,filterFrom:"From",filterMax:"Max",filterMin:"Min",filterTo:"To",firstPage:"First page",goToSlide:(o,e)=>`Go to slide ${o} of ${e}`,hideColumn:"Hide column",hidePassword:"Hide password",hour:"Hour",incompleteDate:"Enter a valid date.",increment:"Increment",jumpBackwardX:o=>`Jump back ${o} pages`,jumpForwardX:o=>`Jump forward ${o} pages`,lastPage:"Last page",loading:"Loading",locked:"Locked",minute:"Minute",month:"Month",moreOptions:"More Options",mute:"Mute",nextDecade:"Next decade",nextMonth:"Next month",nextPage:"Next page",nextSlide:"Next slide",nextVideo:"Next Video",nextYear:"Next year",noData:"No data",noOptions:"No options",noResults:"No matching results",notCompleted:"Not completed",now:"Now",numCharacters:o=>o===1?"1 character":`${o} characters`,numCharactersRemaining:o=>o===1?"1 character remaining":`${o} characters remaining`,numOptionsAvailable:o=>o===0?"No options available":o===1?"1 option available":`${o} options available`,numOptionsSelected:o=>o===0?"No options selected":o===1?"1 option selected":`${o} options selected`,numRowsCopied:o=>o===1?"1 row copied":`${o} rows copied`,numRowsSelected:o=>o===1?"1 row selected":`${o} rows selected`,optionPosition:(o,e,t)=>`${o}, ${e} of ${t}`,optionsLoadError:"Options could not be loaded",pageXOfY:(o,e)=>`Page ${o} of ${e}`,pagination:"Pagination",pause:"Pause",pauseAnimation:"Pause animation",pictureInPicture:"Picture in picture",pinLeft:"Pin left",pinRight:"Pin right",play:"Play",playAnimation:"Play animation",playbackSpeed:"Playback speed",playlist:"Playlist",pm:"PM",previousDecade:"Previous decade",previousMonth:"Previous month",previousPage:"Previous page",previousSlide:"Previous slide",previousVideo:"Previous video",previousYear:"Previous year",progress:"Progress",rangeTooLong:o=>o===1?"Select a range no longer than 1 day":`Select a range no longer than ${o} days`,rangeTooShort:o=>o===1?"Select a range at least 1 day long":`Select a range at least ${o} days long`,readonly:"Read-only",remove:"Remove",resetColumns:"Reset columns",resize:"Resize",resizeColumn:"Resize column",rowsPerPage:"Rows per page",scrollableRegion:"Scrollable region",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",search:"Search",second:"Second",seek:"Seek",seekProgress:(o,e)=>`${o} of ${e}`,selectAColorFromTheScreen:"Select a color from the screen",selectAllRows:"Select all rows",selected:"Selected",selectedDateLabel:o=>`Selected: ${o}`,selectedRangeLabel:o=>`Selected range: ${o}`,selectGroup:"Select group",selectionCleared:"Selection cleared",selectRow:"Select row",showingNofMRows:(o,e)=>`Showing ${o} of ${e} rows`,showingXtoYofZ:(o,e,t)=>`${o}\u2013${e} of ${t}`,showPassword:"Show password",slideNum:o=>`Slide ${o}`,sortAscending:"Sort ascending",sortColumn:"Sort column",sortDescending:"Sort descending",startDate:"Start date",steps:"Steps",stepXOfY:(o,e)=>`Step ${o} of ${e}`,tagAdded:o=>`${o} added`,tagAlreadyAdded:o=>`${o} is already added`,tagInputKeyboardHelp:"Press Backspace or Delete to remove this tag.",tagRemoved:o=>`${o} removed`,time:"Time",timeInputKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the time picker.",today:"Today",toggleColorFormat:"Toggle color format",tooFewTags:o=>o===1?"Add at least 1 tag":`Add at least ${o} tags`,tooManyTags:o=>o===1?"Add no more than 1 tag":`Add no more than ${o} tags`,unmute:"Unmute",unpin:"Unpin",unpinColumn:"Unpin column",videoPlayer:"Video player",volume:"Volume",year:"Year",zoomIn:"Zoom in",zoomOut:"Zoom out"};ne(Zt);var Qt=Zt;var K=class extends Se{lang(){return this.host.didSSR&&!this.host.hasUpdated?this.host.lang||"en":super.lang()}};ne(Qt);var ze=class extends Event{constructor(){super("wa-error",{bubbles:!0,cancelable:!1,composed:!0})}};var Ae=class extends Event{constructor(){super("wa-load",{bubbles:!0,cancelable:!1,composed:!0})}};var ei=g`:host {
  --primary-color: currentColor;
  --primary-opacity: 1;
  --secondary-color: currentColor;
  --secondary-opacity: 0.4;
  --rotate-angle: 0deg;
  box-sizing: content-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: -0.125em;
}
:host(:not([canvas])),
:host([canvas="fixed"]) {
  width: 1.25em;
  height: 1em;
  min-width: 1.25em;
  min-height: 1em;
}
:host([canvas="auto"]),
:host([auto-width]:not([canvas])) {
  width: auto;
  height: 1em;
}
:host([canvas="square"]) {
  width: 1.25em;
  height: 1.25em;
  min-width: 1.25em;
  min-height: 1.25em;
}
:host([canvas="roomy"]) {
  width: 1.5em;
  height: 1.5em;
  min-width: 1.5em;
  min-height: 1.5em;
}
svg {
  height: 1em;
  overflow: visible;
  width: auto;
}
svg path[data-duotone-primary] {
  color: var(--primary-color);
  opacity: var(--path-opacity, var(--primary-opacity));
}
svg path[data-duotone-secondary] {
  color: var(--secondary-color);
  opacity: var(--path-opacity, var(--secondary-opacity));
}
:host([rotate]) {
  transform: rotate(var(--rotate-angle, 0deg));
}
:host([flip="x"]) {
  transform: scaleX(-1);
}
:host([flip="y"]) {
  transform: scaleY(-1);
}
:host([flip="both"]) {
  transform: scale(-1, -1);
}
:host([rotate][flip="x"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scaleX(-1);
}
:host([rotate][flip="y"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scaleY(-1);
}
:host([rotate][flip="both"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scale(-1, -1);
}
:host([animation="beat"]) {
  animation-name: beat;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="bounce"]) {
  animation-name: bounce;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, cubic-bezier(0.28, 0.84, 0.42, 1));
}
:host([animation="fade"]) {
  animation-name: fade;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="beat-fade"]) {
  animation-name: beat-fade;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="flip"]) {
  animation-name: flip;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1.5s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="flip-360"]) {
  animation-name: flip-360;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="shake"]) {
  animation-name: shake;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.75s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="spin"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-pulse"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, steps(8));
}
:host([animation="spin-reverse"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, reverse);
  animation-duration: var(--animation-duration, 2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap"]) {
  animation-name: spin-snap;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 3s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap-4"]) {
  animation-name: spin-snap-4;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 2.4s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap-8"]) {
  animation-name: spin-snap-8;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 4s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="buzz"]) {
  animation-name: buzz;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.6s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="wag"]) {
  animation-name: wag;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.9s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
  transform-origin: bottom center;
}
:host([animation="float"]) {
  animation-name: float;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 3s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
  will-change: transform;
}
:host([animation="swing"]) {
  animation-name: swing;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1.2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
  transform-origin: top center;
}
:host([animation="jello"]) {
  animation-name: jello;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.9s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
}
@media (prefers-reduced-motion: reduce) {
  :host([animation="beat"]),
  :host([animation="bounce"]),
  :host([animation="fade"]),
  :host([animation="beat-fade"]),
  :host([animation="flip"]),
  :host([animation="flip-360"]),
  :host([animation="shake"]),
  :host([animation="spin"]),
  :host([animation="spin-pulse"]),
  :host([animation="spin-reverse"]),
  :host([animation="spin-snap"]),
  :host([animation="spin-snap-4"]),
  :host([animation="spin-snap-8"]),
  :host([animation="buzz"]),
  :host([animation="wag"]),
  :host([animation="float"]),
  :host([animation="swing"]),
  :host([animation="jello"]) {
    animation: none !important;
    transition: none !important;
  }
}
@keyframes beat {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(calc(1.25 * var(--beat-scale, 1.25)));
  }
  45% {
    transform: scale(calc(1.22 * var(--beat-scale, 1.22)));
  }
  65% {
    transform: scale(calc(1.25 * var(--beat-scale, 1.25)));
  }
  90% {
    transform: scale(1);
  }
}
@keyframes bounce {
  0% {
    transform: scale(1, 1) translateY(0);
    animation-timing-function: var(--animation-timing);
  }
  14% {
    transform: scale(var(--bounce-start-scale-x, 1.06), var(--bounce-start-scale-y, 0.94)) translateY(var(--bounce-anticipation, 3px));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  32% {
    transform: scale(var(--bounce-jump-scale-x, 0.94), var(--bounce-jump-scale-y, 1.12)) translateY(calc(-1 * var(--bounce-height, 0.5em)));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  52% {
    transform: scale(1, 1) translateY(calc(-1 * var(--bounce-height, 0.5em) * 1.1));
    animation-timing-function: cubic-bezier(0.5, 0, 1, 0.5);
  }
  70% {
    transform: scale(var(--bounce-land-scale-x, 1.06), var(--bounce-land-scale-y, 0.92)) translateY(0);
    animation-timing-function: cubic-bezier(0.33, 0.33, 0.66, 1);
  }
  85% {
    transform: scale(0.98, 1.04) translateY(calc(-2px * var(--bounce-rebound, 1)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: scale(1, 1) translateY(0);
  }
}
@keyframes fade {
  0% {
    opacity: 1;
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  40% {
    opacity: var(--fade-opacity, 0.4);
    transform: scale(0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes beat-fade {
  0% {
    opacity: var(--beat-fade-opacity, 0.4);
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  25% {
    opacity: calc(var(--beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  45% {
    opacity: 1;
    transform: scale(var(--beat-fade-scale, 1.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  65% {
    opacity: calc(var(--beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: var(--beat-fade-opacity, 0.4);
    transform: scale(1);
  }
}
@keyframes flip {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--flip-anticipation-scale, 0.95)) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  35% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.6));
    animation-timing-function: linear;
  }
  65% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.5));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  92% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * var(--flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), var(--flip-angle, -360deg));
  }
}
@keyframes flip-360 {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--flip-anticipation-scale, 0.95)) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  50% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.6));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  80% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * var(--flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), var(--flip-angle, -360deg));
  }
}
@keyframes shake {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(35deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  20% {
    transform: rotate(-22deg) translateX(-1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  35% {
    transform: rotate(15deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  50% {
    transform: rotate(-9deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  65% {
    transform: rotate(5deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  78% {
    transform: rotate(-3deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  90% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  12% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  16.67% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  28.67% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  33.33% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  45.33% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  62% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  66.67% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  78.67% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  83.33% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  95.33% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap-4 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  15% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  40% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  65% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  90% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap-8 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  9% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  12.5% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  21.5% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  34% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  37.5% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  46.5% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  59% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  62.5% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  71.5% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  84% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  87.5% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  96.5% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes buzz {
  0% {
    transform: translateX(0) rotate(0deg);
    animation-timing-function: cubic-bezier(0.1, 0, 0.9, 1);
  }
  5% {
    transform: translateX(var(--buzz-distance, 4px)) rotate(0.5deg);
  }
  10% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px))) rotate(-0.5deg);
  }
  15% {
    transform: translateX(var(--buzz-distance, 4px)) rotate(0.3deg);
  }
  20% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px))) rotate(-0.3deg);
  }
  25% {
    transform: translateX(calc(var(--buzz-distance, 4px) * 0.7)) rotate(0.2deg);
  }
  30% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px) * 0.7)) rotate(-0.2deg);
  }
  35% {
    transform: translateX(calc(var(--buzz-distance, 4px) * 0.4)) rotate(0.1deg);
  }
  40% {
    transform: translateX(0) rotate(0deg);
  }
  100% {
    transform: translateX(0) rotate(0deg);
  }
}
@keyframes wag {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  12% {
    transform: rotate(var(--wag-angle, 12deg));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  24% {
    transform: rotate(2deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  36% {
    transform: rotate(calc(var(--wag-angle, 12deg) * 0.85));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  48% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  58% {
    transform: rotate(calc(var(--wag-angle, 12deg) * 0.6));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  15% {
    transform: translateY(calc(-0.4 * var(--float-height, 6px))) translateX(var(--float-drift, 1px)) rotate(var(--float-tilt, 1deg)) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  35% {
    transform: translateY(calc(-1 * var(--float-height, 6px))) translateX(0) rotate(0deg) scale(var(--float-stretch-x, 0.98), var(--float-stretch-y, 1.03));
    animation-timing-function: cubic-bezier(0.5, 0, 0.5, 0);
  }
  50% {
    transform: translateY(calc(-0.92 * var(--float-height, 6px))) translateX(calc(-0.5 * var(--float-drift, 1px))) rotate(calc(-0.5 * var(--float-tilt, 1deg))) scale(0.995, 1.01);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  70% {
    transform: translateY(calc(-0.3 * var(--float-height, 6px))) translateX(calc(-1 * var(--float-drift, 1px))) rotate(calc(-1 * var(--float-tilt, 1deg))) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  90% {
    transform: translateY(calc(0.05 * var(--float-height, 6px))) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
  }
}
@keyframes swing {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(var(--swing-angle, 22deg));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  18% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.85));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  28% {
    transform: rotate(calc(var(--swing-angle, 22deg) * 0.65));
    animation-timing-function: cubic-bezier(0.35, 0, 0.65, 1);
  }
  38% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.45));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: rotate(calc(var(--swing-angle, 22deg) * 0.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  56% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.1));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  64% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes jello {
  0% {
    transform: scale(1, 1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  12% {
    transform: scale(var(--jello-scale-x, 1.15), calc(2 - var(--jello-scale-x, 1.15)));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  24% {
    transform: scale(calc(2 - var(--jello-scale-y, 1.12)), var(--jello-scale-y, 1.12));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  36% {
    transform: scale(calc(1 + (var(--jello-scale-x, 1.15) - 1) * 0.5), calc(2 - (1 + (var(--jello-scale-x, 1.15) - 1) * 0.5)));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: scale(calc(2 - (1 + (var(--jello-scale-y, 1.12) - 1) * 0.3)), calc(1 + (var(--jello-scale-y, 1.12) - 1) * 0.3));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  58% {
    transform: scale(1.02, 0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: scale(1, 1);
  }
  100% {
    transform: scale(1, 1);
  }
}
`;var Oi="",Xe="";function ti(){return Oi.replace(/\/$/,"")}function Vi(o){Xe=o}function ii(){if(!Xe){let o=document.querySelector("[data-fa-kit-code]");o&&Vi(o.getAttribute("data-fa-kit-code")||"")}return Xe}var oi="7.3.0";function qi(o,e,t){let i="solid";return e==="chisel"&&(i="chisel-regular"),e==="etch"&&(i="etch-solid"),e==="graphite"&&(i="graphite-thin"),e==="jelly"&&(i="jelly-regular",t==="duo-regular"&&(i="jelly-duo-regular"),t==="fill-regular"&&(i="jelly-fill-regular")),e==="jelly-duo"&&(i="jelly-duo-regular"),e==="jelly-fill"&&(i="jelly-fill-regular"),e==="notdog"&&(t==="solid"&&(i="notdog-solid"),t==="duo-solid"&&(i="notdog-duo-solid")),e==="notdog-duo"&&(i="notdog-duo-solid"),e==="slab"&&((t==="solid"||t==="regular")&&(i="slab-regular"),t==="press-regular"&&(i="slab-press-regular")),e==="slab-press"&&(i="slab-press-regular"),e==="slab-duo"&&(i="slab-duo-regular"),e==="slab-press-duo"&&(i="slab-press-duo-regular"),e==="thumbprint"&&(i="thumbprint-light"),e==="utility"&&(i="utility-semibold"),e==="utility-duo"&&(i="utility-duo-semibold"),e==="utility-fill"&&(i="utility-fill-semibold"),e==="whiteboard"&&(i="whiteboard-semibold"),e==="mosaic"&&(i="mosaic-solid"),e==="pixel"&&(i="pixel-regular"),e==="vellum"&&(i="vellum-solid"),e==="classic"&&(t==="thin"&&(i="thin"),t==="light"&&(i="light"),t==="regular"&&(i="regular"),t==="solid"&&(i="solid")),e==="duotone"&&(t==="thin"&&(i="duotone-thin"),t==="light"&&(i="duotone-light"),t==="regular"&&(i="duotone-regular"),t==="solid"&&(i="duotone")),e==="sharp"&&(t==="thin"&&(i="sharp-thin"),t==="light"&&(i="sharp-light"),t==="regular"&&(i="sharp-regular"),t==="solid"&&(i="sharp-solid")),e==="sharp-duotone"&&(t==="thin"&&(i="sharp-duotone-thin"),t==="light"&&(i="sharp-duotone-light"),t==="regular"&&(i="sharp-duotone-regular"),t==="solid"&&(i="sharp-duotone-solid")),e==="brands"&&(i="brands"),i}function Ni(o,e,t){let i=qi(o,e,t),r=ti();if(r)return`${r}/${i}/${o}.svg`;let a=ii();return a.length>0?`https://ka-p.fontawesome.com/releases/v${oi}/svgs/${i}/${o}.svg?token=${encodeURIComponent(a)}`:`https://ka-f.fontawesome.com/releases/v${oi}/svgs/${i}/${o}.svg`}var Hi={name:"default",resolver:(o,e="classic",t="solid")=>Ni(o,e,t),mutator:(o,e)=>{if(o.hasAttribute("fill")||o.setAttribute("fill","currentColor"),e?.family&&!o.hasAttribute("data-duotone-initialized")){let{family:t,variant:i}=e;if(t==="duotone"||t==="sharp-duotone"||t==="notdog-duo"||t==="notdog"&&i==="duo-solid"||t==="jelly-duo"||t==="jelly"&&i==="duo-regular"||t==="utility-duo"||t==="slab-duo"||t==="slab-press-duo"||t==="thumbprint"){let r=[...o.querySelectorAll("path")],a=r.find(n=>!n.hasAttribute("opacity")),s=r.find(n=>n.hasAttribute("opacity"));if(!a||!s)return;if(a.setAttribute("data-duotone-primary",""),s.setAttribute("data-duotone-secondary",""),e.swapOpacity&&a&&s){let n=s.getAttribute("opacity")||"0.4";a.style.setProperty("--path-opacity",n),s.style.setProperty("--path-opacity","1")}o.setAttribute("data-duotone-initialized","")}}}},ri=Hi;function Ui(o){return`data:image/svg+xml,${encodeURIComponent(o)}`}var Ye={solid:{"arrow-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M169.4 502.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 402.7 224 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 370.7-105.4-105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/></svg>',"arrow-up":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M214.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 480c0 17.7 14.3 32 32 32s32-14.3 32-32l0-370.7 105.4 105.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/></svg>',backward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M236.3 107.1C247.9 96 265 92.9 279.7 99.2C294.4 105.5 304 120 304 136L304 272.3L476.3 107.2C487.9 96 505 92.9 519.7 99.2C534.4 105.5 544 120 544 136L544 504C544 520 534.4 534.5 519.7 540.8C505 547.1 487.9 544 476.3 532.9L304 367.7L304 504C304 520 294.4 534.5 279.7 540.8C265 547.1 247.9 544 236.3 532.9L44.3 348.9C36.5 341.3 32 330.9 32 320C32 309.1 36.5 298.7 44.3 291.1L236.3 107.1z"/></svg>',"backward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M491 100.8C478.1 93.8 462.3 94.5 450 102.6L192 272.1L192 128C192 110.3 177.7 96 160 96C142.3 96 128 110.3 128 128L128 512C128 529.7 142.3 544 160 544C177.7 544 192 529.7 192 512L192 367.9L450 537.5C462.3 545.6 478 546.3 491 539.3C504 532.3 512 518.8 512 504.1L512 136.1C512 121.4 503.9 107.9 491 100.9z"/></svg>',bars:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.3.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc. --><path d="M0 96C0 78.3 14.3 64 32 64l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 128C14.3 128 0 113.7 0 96zM0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32zM448 416c0 17.7-14.3 32-32 32L32 448c-17.7 0-32-14.3-32-32s14.3-32 32-32l384 0c17.7 0 32 14.3 32 32z"/></svg>',"angles-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M77.3 256 214.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256zm192 0L406.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L269.3 256z"/></svg>',"angles-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.7 256 297.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L434.7 256zm-192 0L105.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256z"/></svg>',check:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.8 70.1c14.3 10.4 17.5 30.4 7.1 44.7l-256 352c-5.5 7.6-14 12.3-23.4 13.1s-18.5-2.7-25.1-9.3l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l101.5 101.5 234-321.7c10.4-14.3 30.4-17.5 44.7-7.1z"/></svg>',"chevron-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M201.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 338.7 54.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"/></svg>',"chevron-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"/></svg>',"chevron-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M311.1 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L243.2 256 73.9 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"/></svg>',circle:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0z"/></svg>',"closed-captioning":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M64 192C64 156.7 92.7 128 128 128L512 128C547.3 128 576 156.7 576 192L576 448C576 483.3 547.3 512 512 512L128 512C92.7 512 64 483.3 64 448L64 192zM216 272L248 272C252.4 272 256 275.6 256 280C256 293.3 266.7 304 280 304C293.3 304 304 293.3 304 280C304 249.1 278.9 224 248 224L216 224C185.1 224 160 249.1 160 280L160 360C160 390.9 185.1 416 216 416L248 416C278.9 416 304 390.9 304 360C304 346.7 293.3 336 280 336C266.7 336 256 346.7 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 280C208 275.6 211.6 272 216 272zM384 280C384 275.6 387.6 272 392 272L424 272C428.4 272 432 275.6 432 280C432 293.3 442.7 304 456 304C469.3 304 480 293.3 480 280C480 249.1 454.9 224 424 224L392 224C361.1 224 336 249.1 336 280L336 360C336 390.9 361.1 416 392 416L424 416C454.9 416 480 390.9 480 360C480 346.7 469.3 336 456 336C442.7 336 432 346.7 432 360C432 364.4 428.4 368 424 368L392 368C387.6 368 384 364.4 384 360L384 280z"/></svg>',"closed-captioning-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M39 39.1C48.4 29.7 63.6 29.7 72.9 39.1L161.8 128L512 128C547.3 128 576 156.7 576 192L576 448C576 473.5 561.1 495.4 539.6 505.8L601 567.1C610.4 576.5 610.4 591.7 601 601C591.6 610.3 576.4 610.4 567.1 601L39 73.1C29.7 63.7 29.7 48.5 39 39.1zM384 350.1L384 279.9C384 275.5 387.6 271.9 392 271.9L424 271.9C428.4 271.9 432 275.5 432 279.9C432 293.2 442.7 303.9 456 303.9C469.3 303.9 480 293.2 480 279.9C480 249 454.9 223.9 424 223.9L392 223.9C361.1 223.9 336 249 336 279.9L336 302.1L384 350.1zM445.5 411.6C465.7 403.2 480 383.2 480 359.9C480 346.6 469.3 335.9 456 335.9C442.7 335.9 432 346.6 432 359.9C432 364.3 428.4 367.9 424 367.9L401.8 367.9L445.5 411.6zM162.3 264.1C160.8 269.1 160 274.5 160 280L160 360C160 390.9 185.1 416 216 416L248 416C266.1 416 282.1 407.5 292.4 394.2L410.2 512L128 512C92.7 512 64 483.3 64 448L64 192C64 184.2 65.4 176.7 68 169.8L162.3 264.1zM256.1 357.9C256 358.6 256 359.3 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 309.8L256.1 357.9z"/></svg>',compress:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M160 64c0-17.7-14.3-32-32-32S96 46.3 96 64l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96zM32 320c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM352 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 320c-17.7 0-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0z"/></svg>',ellipsis:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 320C96 289.1 121.1 264 152 264C182.9 264 208 289.1 208 320C208 350.9 182.9 376 152 376C121.1 376 96 350.9 96 320zM264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320zM488 264C518.9 264 544 289.1 544 320C544 350.9 518.9 376 488 376C457.1 376 432 350.9 432 320C432 289.1 457.1 264 488 264z"/></svg>',"ellipsis-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M320 208C289.1 208 264 182.9 264 152C264 121.1 289.1 96 320 96C350.9 96 376 121.1 376 152C376 182.9 350.9 208 320 208zM320 432C350.9 432 376 457.1 376 488C376 518.9 350.9 544 320 544C289.1 544 264 518.9 264 488C264 457.1 289.1 432 320 432zM376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320z"/></svg>',expand:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 96C110.3 96 96 110.3 96 128L96 224C96 241.7 110.3 256 128 256C145.7 256 160 241.7 160 224L160 160L224 160C241.7 160 256 145.7 256 128C256 110.3 241.7 96 224 96L128 96zM160 416C160 398.3 145.7 384 128 384C110.3 384 96 398.3 96 416L96 512C96 529.7 110.3 544 128 544L224 544C241.7 544 256 529.7 256 512C256 494.3 241.7 480 224 480L160 480L160 416zM416 96C398.3 96 384 110.3 384 128C384 145.7 398.3 160 416 160L480 160L480 224C480 241.7 494.3 256 512 256C529.7 256 544 241.7 544 224L544 128C544 110.3 529.7 96 512 96L416 96zM544 416C544 398.3 529.7 384 512 384C494.3 384 480 398.3 480 416L480 480L416 480C398.3 480 384 494.3 384 512C384 529.7 398.3 544 416 544L512 544C529.7 544 544 529.7 544 512L544 416z"/></svg>',eyedropper:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M341.6 29.2l-101.6 101.6-9.4-9.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-9.4-9.4 101.6-101.6c39-39 39-102.2 0-141.1s-102.2-39-141.1 0zM55.4 323.3c-15 15-23.4 35.4-23.4 56.6l0 42.4-26.6 39.9c-8.5 12.7-6.8 29.6 4 40.4s27.7 12.5 40.4 4l39.9-26.6 42.4 0c21.2 0 41.6-8.4 56.6-23.4l109.4-109.4-45.3-45.3-109.4 109.4c-3 3-7.1 4.7-11.3 4.7l-36.1 0 0-36.1c0-4.2 1.7-8.3 4.7-11.3l109.4-109.4-45.3-45.3-109.4 109.4z"/></svg>',filter:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 64C19.1 64 7.4 71.8 2.4 83.8S.2 109.5 9.4 118.6L192 301.3 192 416c0 8.5 3.4 16.6 9.4 22.6l64 64c9.2 9.2 22.9 11.9 34.9 6.9S320 492.9 320 480l0-178.7 182.6-182.6c9.2-9.2 11.9-22.9 6.9-34.9S492.9 64 480 64L32 64z"/></svg>',forward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M403.7 107.1C392.1 96 375 92.9 360.3 99.2C345.6 105.5 336 120 336 136L336 272.3L163.7 107.2C152.1 96 135 92.9 120.3 99.2C105.6 105.5 96 120 96 136L96 504C96 520 105.6 534.5 120.3 540.8C135 547.1 152.1 544 163.7 532.9L336 367.7L336 504C336 520 345.6 534.5 360.3 540.8C375 547.1 392.1 544 403.7 532.9L595.7 348.9C603.6 341.4 608 330.9 608 320C608 309.1 603.5 298.7 595.7 291.1L403.7 107.1z"/></svg>',file:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M192 64C156.7 64 128 92.7 128 128L128 512C128 547.3 156.7 576 192 576L448 576C483.3 576 512 547.3 512 512L512 234.5C512 217.5 505.3 201.2 493.3 189.2L386.7 82.7C374.7 70.7 358.5 64 341.5 64L192 64zM453.5 240L360 240C346.7 240 336 229.3 336 216L336 122.5L453.5 240z"/></svg>',"file-audio":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM389.8 307.7C380.7 301.4 368.3 303.6 362 312.7C355.7 321.8 357.9 334.2 367 340.5C390.9 357.2 406.4 384.8 406.4 416C406.4 447.2 390.8 474.9 367 491.5C357.9 497.8 355.7 510.3 362 519.3C368.3 528.3 380.8 530.6 389.8 524.3C423.9 500.5 446.4 460.8 446.4 416C446.4 371.2 424 331.5 389.8 307.7zM208 376C199.2 376 192 383.2 192 392L192 440C192 448.8 199.2 456 208 456L232 456L259.2 490C262.2 493.8 266.8 496 271.7 496L272 496C280.8 496 288 488.8 288 480L288 352C288 343.2 280.8 336 272 336L271.7 336C266.8 336 262.2 338.2 259.2 342L232 376L208 376zM336 448.2C336 458.9 346.5 466.4 354.9 459.8C367.8 449.5 376 433.7 376 416C376 398.3 367.8 382.5 354.9 372.2C346.5 365.5 336 373.1 336 383.8L336 448.3z"/></svg>',"file-code":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM282.2 359.6C290.8 349.5 289.7 334.4 279.6 325.8C269.5 317.2 254.4 318.3 245.8 328.4L197.8 384.4C190.1 393.4 190.1 406.6 197.8 415.6L245.8 471.6C254.4 481.7 269.6 482.8 279.6 474.2C289.6 465.6 290.8 450.4 282.2 440.4L247.6 400L282.2 359.6zM394.2 328.4C385.6 318.3 370.4 317.2 360.4 325.8C350.4 334.4 349.2 349.6 357.8 359.6L392.4 400L357.8 440.4C349.2 450.5 350.3 465.6 360.4 474.2C370.5 482.8 385.6 481.7 394.2 471.6L442.2 415.6C449.9 406.6 449.9 393.4 442.2 384.4L394.2 328.4z"/></svg>',"file-excel":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM292 330.7C284.6 319.7 269.7 316.7 258.7 324C247.7 331.3 244.7 346.3 252 357.3L291.2 416L252 474.7C244.6 485.7 247.6 500.6 258.7 508C269.8 515.4 284.6 512.4 292 501.3L320 459.3L348 501.3C355.4 512.3 370.3 515.3 381.3 508C392.3 500.7 395.3 485.7 388 474.7L348.8 416L388 357.3C395.4 346.3 392.4 331.4 381.3 324C370.2 316.6 355.4 319.6 348 330.7L320 372.7L292 330.7z"/></svg>',"file-image":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM256 320C256 302.3 241.7 288 224 288C206.3 288 192 302.3 192 320C192 337.7 206.3 352 224 352C241.7 352 256 337.7 256 320zM220.6 512L419.4 512C435.2 512 448 499.2 448 483.4C448 476.1 445.2 469 440.1 463.7L343.3 361.9C337.3 355.6 328.9 352 320.1 352L319.8 352C311 352 302.7 355.6 296.6 361.9L199.9 463.7C194.8 469 192 476.1 192 483.4C192 499.2 204.8 512 220.6 512z"/></svg>',"file-pdf":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 64C92.7 64 64 92.7 64 128L64 512C64 547.3 92.7 576 128 576L208 576L208 464C208 428.7 236.7 400 272 400L448 400L448 234.5C448 217.5 441.3 201.2 429.3 189.2L322.7 82.7C310.7 70.7 294.5 64 277.5 64L128 64zM389.5 240L296 240C282.7 240 272 229.3 272 216L272 122.5L389.5 240zM272 444C261 444 252 453 252 464L252 592C252 603 261 612 272 612C283 612 292 603 292 592L292 564L304 564C337.1 564 364 537.1 364 504C364 470.9 337.1 444 304 444L272 444zM304 524L292 524L292 484L304 484C315 484 324 493 324 504C324 515 315 524 304 524zM400 444C389 444 380 453 380 464L380 592C380 603 389 612 400 612L432 612C460.7 612 484 588.7 484 560L484 496C484 467.3 460.7 444 432 444L400 444zM420 572L420 484L432 484C438.6 484 444 489.4 444 496L444 560C444 566.6 438.6 572 432 572L420 572zM508 464L508 592C508 603 517 612 528 612C539 612 548 603 548 592L548 548L576 548C587 548 596 539 596 528C596 517 587 508 576 508L548 508L548 484L576 484C587 484 596 475 596 464C596 453 587 444 576 444L528 444C517 444 508 453 508 464z"/></svg>',"file-powerpoint":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM280 320C266.7 320 256 330.7 256 344L256 488C256 501.3 266.7 512 280 512C293.3 512 304 501.3 304 488L304 464L328 464C367.8 464 400 431.8 400 392C400 352.2 367.8 320 328 320L280 320zM328 416L304 416L304 368L328 368C341.3 368 352 378.7 352 392C352 405.3 341.3 416 328 416z"/></svg>',"file-video":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM208 368L208 464C208 481.7 222.3 496 240 496L336 496C353.7 496 368 481.7 368 464L368 440L403 475C406.2 478.2 410.5 480 415 480C424.4 480 432 472.4 432 463L432 368.9C432 359.5 424.4 351.9 415 351.9C410.5 351.9 406.2 353.7 403 356.9L368 391.9L368 367.9C368 350.2 353.7 335.9 336 335.9L240 335.9C222.3 335.9 208 350.2 208 367.9z"/></svg>',"file-word":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM263.4 338.8C260.5 325.9 247.7 317.7 234.8 320.6C221.9 323.5 213.7 336.3 216.6 349.2L248.6 493.2C250.9 503.7 260 511.4 270.8 512C281.6 512.6 291.4 505.9 294.8 495.6L320 419.9L345.2 495.6C348.6 505.8 358.4 512.5 369.2 512C380 511.5 389.1 503.8 391.4 493.2L423.4 349.2C426.3 336.3 418.1 323.4 405.2 320.6C392.3 317.8 379.4 325.9 376.6 338.8L363.4 398.2L342.8 336.4C339.5 326.6 330.4 320 320 320C309.6 320 300.5 326.6 297.2 336.4L276.6 398.2L263.4 338.8z"/></svg>',"file-zipper":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM192 136C192 149.3 202.7 160 216 160L264 160C277.3 160 288 149.3 288 136C288 122.7 277.3 112 264 112L216 112C202.7 112 192 122.7 192 136zM192 232C192 245.3 202.7 256 216 256L264 256C277.3 256 288 245.3 288 232C288 218.7 277.3 208 264 208L216 208C202.7 208 192 218.7 192 232zM256 304L224 304C206.3 304 192 318.3 192 336L192 384C192 410.5 213.5 432 240 432C266.5 432 288 410.5 288 384L288 336C288 318.3 273.7 304 256 304zM240 368C248.8 368 256 375.2 256 384C256 392.8 248.8 400 240 400C231.2 400 224 392.8 224 384C224 375.2 231.2 368 240 368z"/></svg>',"forward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M21 36.8c12.9-7 28.7-6.3 41 1.8L320 208.1 320 64c0-17.7 14.3-32 32-32s32 14.3 32 32l0 384c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-144.1-258 169.6c-12.3 8.1-28 8.8-41 1.8S0 454.7 0 440L0 72C0 57.3 8.1 43.8 21 36.8z"/></svg>',gauge:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm320 96c0-26.9-16.5-49.9-40-59.3L280 120c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 172.7c-23.5 9.5-40 32.5-40 59.3 0 35.3 28.7 64 64 64s64-28.7 64-64zM144 176a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm-16 80a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM400 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>',gear:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M259.1 73.5C262.1 58.7 275.2 48 290.4 48L350.2 48C365.4 48 378.5 58.7 381.5 73.5L396 143.5C410.1 149.5 423.3 157.2 435.3 166.3L503.1 143.8C517.5 139 533.3 145 540.9 158.2L570.8 210C578.4 223.2 575.7 239.8 564.3 249.9L511 297.3C511.9 304.7 512.3 312.3 512.3 320C512.3 327.7 511.8 335.3 511 342.7L564.4 390.2C575.8 400.3 578.4 417 570.9 430.1L541 481.9C533.4 495 517.6 501.1 503.2 496.3L435.4 473.8C423.3 482.9 410.1 490.5 396.1 496.6L381.7 566.5C378.6 581.4 365.5 592 350.4 592L290.6 592C275.4 592 262.3 581.3 259.3 566.5L244.9 496.6C230.8 490.6 217.7 482.9 205.6 473.8L137.5 496.3C123.1 501.1 107.3 495.1 99.7 481.9L69.8 430.1C62.2 416.9 64.9 400.3 76.3 390.2L129.7 342.7C128.8 335.3 128.4 327.7 128.4 320C128.4 312.3 128.9 304.7 129.7 297.3L76.3 249.8C64.9 239.7 62.3 223 69.8 209.9L99.7 158.1C107.3 144.9 123.1 138.9 137.5 143.7L205.3 166.2C217.4 157.1 230.6 149.5 244.6 143.4L259.1 73.5zM320.3 400C364.5 399.8 400.2 363.9 400 319.7C399.8 275.5 363.9 239.8 319.7 240C275.5 240.2 239.8 276.1 240 320.3C240.2 364.5 276.1 400.2 320.3 400z"/></svg>',"grip-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M128 40c0-22.1-17.9-40-40-40L40 0C17.9 0 0 17.9 0 40L0 88c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM0 424l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 40c0-22.1-17.9-40-40-40L232 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM192 232l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 424c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48z"/></svg>',indeterminate:'<svg part="indeterminate-icon" class="icon" viewBox="0 0 16 16"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round"><g stroke="currentColor" stroke-width="2"><g transform="translate(2.285714 6.857143)"><path d="M10.2857143,1.14285714 L1.14285714,1.14285714"/></g></g></g></svg>',"magnifying-glass":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376C296.3 401.1 253.9 416 208 416 93.1 416 0 322.9 0 208S93.1 0 208 0 416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>',minus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32z"/></svg>',pause:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M48 32C21.5 32 0 53.5 0 80L0 432c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48L48 32zm224 0c-26.5 0-48 21.5-48 48l0 352c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48l-64 0z"/></svg>',"picture-in-picture":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M448 32c35.3 0 64 28.7 64 64l0 112-64 0 0-112-384 0 0 320 144 0 0 64-144 0-6.5-.3c-30.1-3.1-54.1-27-57.1-57.1L0 416 0 96C0 62.9 25.2 35.6 57.5 32.3L64 32 448 32zm16 224c26.5 0 48 21.5 48 48l0 128c0 26.5-21.5 48-48 48l-160 0c-26.5 0-48-21.5-48-48l0-128c0-26.5 21.5-48 48-48l160 0z"/></svg>',play:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M91.2 36.9c-12.4-6.8-27.4-6.5-39.6 .7S32 57.9 32 72l0 368c0 14.1 7.5 27.2 19.6 34.4s27.2 7.5 39.6 .7l336-184c12.8-7 20.8-20.5 20.8-35.1s-8-28.1-20.8-35.1l-336-184z"/></svg>',"play-circle":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zM188.3 147.1c-7.6 4.2-12.3 12.3-12.3 20.9l0 176c0 8.7 4.7 16.7 12.3 20.9s16.8 4.1 24.3-.5l144-88c7.1-4.4 11.5-12.1 11.5-20.5s-4.4-16.1-11.5-20.5l-144-88c-7.4-4.5-16.7-4.7-24.3-.5z"/></svg>',plus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 128C352 110.3 337.7 96 320 96C302.3 96 288 110.3 288 128L288 288L128 288C110.3 288 96 302.3 96 320C96 337.7 110.3 352 128 352L288 352L288 512C288 529.7 302.3 544 320 544C337.7 544 352 529.7 352 512L352 352L512 352C529.7 352 544 337.7 544 320C544 302.3 529.7 288 512 288L352 288L352 128z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M309.5-18.9c-4.1-8-12.4-13.1-21.4-13.1s-17.3 5.1-21.4 13.1L193.1 125.3 33.2 150.7c-8.9 1.4-16.3 7.7-19.1 16.3s-.5 18 5.8 24.4l114.4 114.5-25.2 159.9c-1.4 8.9 2.3 17.9 9.6 23.2s16.9 6.1 25 2L288.1 417.6 432.4 491c8 4.1 17.7 3.3 25-2s11-14.2 9.6-23.2L441.7 305.9 556.1 191.4c6.4-6.4 8.6-15.8 5.8-24.4s-10.1-14.9-19.1-16.3L383 125.3 309.5-18.9z"/></svg>',"table-columns":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 96C0 60.7 28.7 32 64 32l320 0c35.3 0 64 28.7 64 64l0 320c0 35.3-28.7 64-64 64L64 480c-35.3 0-64-28.7-64-64L0 96zm64 64l0 256 128 0 0-256-128 0zm320 0l-128 0 0 256 128 0 0-256z"/></svg>',thumbtack:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 32C32 14.3 46.3 0 64 0L320 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-29.5 0 10.3 134.1c37.1 21.2 65.8 56.4 78.2 99.7l3.8 13.4c2.8 9.7 .8 20-5.2 28.1S362 352 352 352L32 352c-10 0-19.5-4.7-25.5-12.7s-8-18.4-5.2-28.1L5 297.8c12.4-43.3 41-78.5 78.2-99.7L93.5 64 64 64C46.3 64 32 49.7 32 32zM160 400l64 0 0 112c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-112z"/></svg>',"up-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M406.6 502.6l96-96c9.2-9.2 11.9-22.9 6.9-34.9S492.9 352 480 352l-64 0 0-320c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 320-64 0c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l96 96c12.5 12.5 32.8 12.5 45.3 0zM150.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-96 96c-9.2 9.2-11.9 22.9-6.9 34.9S19.1 160 32 160l64 0 0 320c0 17.7 14.3 32 32 32s32-14.3 32-32l0-320 64 0c12.9 0 24.6-7.8 29.6-19.8s2.2-25.7-6.9-34.9l-96-96z"/></svg>',upload:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 173.3L352 384C352 401.7 337.7 416 320 416C302.3 416 288 401.7 288 384L288 173.3L246.6 214.7C234.1 227.2 213.8 227.2 201.3 214.7C188.8 202.2 188.8 181.9 201.3 169.4L297.3 73.4C309.8 60.9 330.1 60.9 342.6 73.4L438.6 169.4C451.1 181.9 451.1 202.2 438.6 214.7C426.1 227.2 405.8 227.2 393.3 214.7L352 173.3zM320 464C364.2 464 400 428.2 400 384L480 384C515.3 384 544 412.7 544 448L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 448C96 412.7 124.7 384 160 384L240 384C240 428.2 275.8 464 320 464zM464 488C477.3 488 488 477.3 488 464C488 450.7 477.3 440 464 440C450.7 440 440 450.7 440 464C440 477.3 450.7 488 464 488z"/></svg>',user:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M224 248a120 120 0 1 0 0-240 120 120 0 1 0 0 240zm-29.7 56C95.8 304 16 383.8 16 482.3 16 498.7 29.3 512 45.7 512l356.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-59.4 0z"/></svg>',volume:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM441.1 107c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C443.3 170.7 464 210.9 464 256s-20.7 85.3-53.2 111.8c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5c43.2-35.2 70.9-88.9 70.9-149s-27.7-113.8-70.9-149zm-60.5 74.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-low":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM380.6 181.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM367 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',xmark:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M55.1 73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L147.2 256 9.9 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192.5 301.3 329.9 438.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.8 256 375.1 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192.5 210.7 55.1 73.4z"/></svg>'},regular:{calendar:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M216 64C229.3 64 240 74.7 240 88L240 128L400 128L400 88C400 74.7 410.7 64 424 64C437.3 64 448 74.7 448 88L448 128L480 128C515.3 128 544 156.7 544 192L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 192C96 156.7 124.7 128 160 128L192 128L192 88C192 74.7 202.7 64 216 64zM216 176L160 176C151.2 176 144 183.2 144 192L144 240L496 240L496 192C496 183.2 488.8 176 480 176L216 176zM144 288L144 480C144 488.8 151.2 496 160 496L480 496C488.8 496 496 488.8 496 480L496 288L144 288z"/></svg>',"circle-question":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M464 256a208 208 0 1 0 -416 0 208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm256-80c-17.7 0-32 14.3-32 32 0 13.3-10.7 24-24 24s-24-10.7-24-24c0-44.2 35.8-80 80-80s80 35.8 80 80c0 47.2-36 67.2-56 74.5l0 3.8c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-8.1c0-20.5 14.8-35.2 30.1-40.2 6.4-2.1 13.2-5.5 18.2-10.3 4.3-4.2 7.7-10 7.7-19.6 0-17.7-14.3-32-32-32zM224 368a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>',"circle-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM167 167c-9.4 9.4-9.4 24.6 0 33.9l55 55-55 55c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l55-55 55 55c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-55-55 55-55c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-55 55-55-55c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',clock:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M528 320C528 434.9 434.9 528 320 528C205.1 528 112 434.9 112 320C112 205.1 205.1 112 320 112C434.9 112 528 205.1 528 320zM64 320C64 461.4 178.6 576 320 576C461.4 576 576 461.4 576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320zM296 184L296 320C296 328 300 335.5 306.7 340L402.7 404C413.7 411.4 428.6 408.4 436 397.3C443.4 386.2 440.4 371.4 429.3 364L344 307.2L344 184C344 170.7 333.3 160 320 160C306.7 160 296 170.7 296 184z"/></svg>',copy:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M384 336l-192 0c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l133.5 0c4.2 0 8.3 1.7 11.3 4.7l58.5 58.5c3 3 4.7 7.1 4.7 11.3L400 320c0 8.8-7.2 16-16 16zM192 384l192 0c35.3 0 64-28.7 64-64l0-197.5c0-17-6.7-33.3-18.7-45.3L370.7 18.7C358.7 6.7 342.5 0 325.5 0L192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-48 0 0 16c0 8.8-7.2 16-16 16L64 464c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l16 0 0-48-16 0z"/></svg>',eye:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288 80C222.8 80 169.2 109.6 128.1 147.7 89.6 183.5 63 226 49.4 256 63 286 89.6 328.5 128.1 364.3 169.2 402.4 222.8 432 288 432s118.8-29.6 159.9-67.7C486.4 328.5 513 286 526.6 256 513 226 486.4 183.5 447.9 147.7 406.8 109.6 353.2 80 288 80zM95.4 112.6C142.5 68.8 207.2 32 288 32s145.5 36.8 192.6 80.6c46.8 43.5 78.1 95.4 93 131.1 3.3 7.9 3.3 16.7 0 24.6-14.9 35.7-46.2 87.7-93 131.1-47.1 43.7-111.8 80.6-192.6 80.6S142.5 443.2 95.4 399.4c-46.8-43.5-78.1-95.4-93-131.1-3.3-7.9-3.3-16.7 0-24.6 14.9-35.7 46.2-87.7 93-131.1zM288 336c44.2 0 80-35.8 80-80 0-29.6-16.1-55.5-40-69.3-1.4 59.7-49.6 107.9-109.3 109.3 13.8 23.9 39.7 40 69.3 40zm-79.6-88.4c2.5 .3 5 .4 7.6 .4 35.3 0 64-28.7 64-64 0-2.6-.2-5.1-.4-7.6-37.4 3.9-67.2 33.7-71.1 71.1zm45.6-115c10.8-3 22.2-4.5 33.9-4.5 8.8 0 17.5 .9 25.8 2.6 .3 .1 .5 .1 .8 .2 57.9 12.2 101.4 63.7 101.4 125.2 0 70.7-57.3 128-128 128-61.6 0-113-43.5-125.2-101.4-1.8-8.6-2.8-17.5-2.8-26.6 0-11 1.4-21.8 4-32 .2-.7 .3-1.3 .5-1.9 11.9-43.4 46.1-77.6 89.5-89.5z"/></svg>',"eye-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M41-24.9c-9.4-9.4-24.6-9.4-33.9 0S-2.3-.3 7 9.1l528 528c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-96.4-96.4c2.7-2.4 5.4-4.8 8-7.2 46.8-43.5 78.1-95.4 93-131.1 3.3-7.9 3.3-16.7 0-24.6-14.9-35.7-46.2-87.7-93-131.1-47.1-43.7-111.8-80.6-192.6-80.6-56.8 0-105.6 18.2-146 44.2L41-24.9zM176.9 111.1c32.1-18.9 69.2-31.1 111.1-31.1 65.2 0 118.8 29.6 159.9 67.7 38.5 35.7 65.1 78.3 78.6 108.3-13.6 30-40.2 72.5-78.6 108.3-3.1 2.8-6.2 5.6-9.4 8.4L393.8 328c14-20.5 22.2-45.3 22.2-72 0-70.7-57.3-128-128-128-26.7 0-51.5 8.2-72 22.2l-39.1-39.1zm182 182l-108-108c11.1-5.8 23.7-9.1 37.1-9.1 44.2 0 80 35.8 80 80 0 13.4-3.3 26-9.1 37.1zM103.4 173.2l-34-34c-32.6 36.8-55 75.8-66.9 104.5-3.3 7.9-3.3 16.7 0 24.6 14.9 35.7 46.2 87.7 93 131.1 47.1 43.7 111.8 80.6 192.6 80.6 37.3 0 71.2-7.9 101.5-20.6L352.2 422c-20 6.4-41.4 10-64.2 10-65.2 0-118.8-29.6-159.9-67.7-38.5-35.7-65.1-78.3-78.6-108.3 10.4-23.1 28.6-53.6 54-82.8z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288.1-32c9 0 17.3 5.1 21.4 13.1L383 125.3 542.9 150.7c8.9 1.4 16.3 7.7 19.1 16.3s.5 18-5.8 24.4L441.7 305.9 467 465.8c1.4 8.9-2.3 17.9-9.6 23.2s-17 6.1-25 2L288.1 417.6 143.8 491c-8 4.1-17.7 3.3-25-2s-11-14.2-9.6-23.2L134.4 305.9 20 191.4c-6.4-6.4-8.6-15.8-5.8-24.4s10.1-14.9 19.1-16.3l159.9-25.4 73.6-144.2c4.1-8 12.4-13.1 21.4-13.1zm0 76.8L230.3 158c-3.5 6.8-10 11.6-17.6 12.8l-125.5 20 89.8 89.9c5.4 5.4 7.9 13.1 6.7 20.7l-19.8 125.5 113.3-57.6c6.8-3.5 14.9-3.5 21.8 0l113.3 57.6-19.8-125.5c-1.2-7.6 1.3-15.3 6.7-20.7l89.8-89.9-125.5-20c-7.6-1.2-14.1-6-17.6-12.8L288.1 44.8z"/></svg>'}},ji={name:"system",resolver:(o,e="classic",t="solid")=>{let r=Ye[t][o]??Ye.regular[o]??Ye.regular["circle-question"];return r?Ui(r):""},mutator:o=>{o.hasAttribute("fill")||o.setAttribute("fill","currentColor")}},ai=ji;var Wi="classic",Xi=[ri,ai],si=new Set;function ni(o){si.add(o)}function ci(o){si.delete(o)}function _e(o){return Xi.find(e=>e.name===o)}function li(){return Wi}var Yi=Object.defineProperty,Ki=Object.getOwnPropertyDescriptor,b=(o,e,t,i)=>{for(var r=i>1?void 0:i?Ki(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&Yi(e,t,r),r},ce=Symbol(),Ee=Symbol(),Ke,Ge=new Map,w=class extends ${constructor(){super(...arguments),this.svg=null,this.autoWidth=!1,this.swapOpacity=!1,this.label="",this.library="default",this.rotate=0,this.resolveIcon=async(o,e)=>{let t;if(e?.spriteSheet){this.hasUpdated||await this.updateComplete,this.svg=h`<svg part="svg">
        <use part="use" href="${o}"></use>
      </svg>`,await this.updateComplete;let i=this.shadowRoot.querySelector("[part='svg']");return typeof e.mutator=="function"&&e.mutator(i,this),this.svg}try{if(t=await fetch(o,{mode:"cors"}),!t.ok)return t.status===410?ce:Ee}catch{return Ee}try{let i=document.createElement("div");i.innerHTML=await t.text();let r=i.firstElementChild;if(r?.tagName?.toLowerCase()!=="svg")return ce;Ke||(Ke=new DOMParser);let s=Ke.parseFromString(r.outerHTML,"text/html").body.querySelector("svg");return s?(s.part.add("svg"),document.adoptNode(s)):ce}catch{return ce}}}connectedCallback(){super.connectedCallback(),ni(this)}firstUpdated(o){super.firstUpdated(o),this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`),this.setIcon()}disconnectedCallback(){super.disconnectedCallback(),ci(this)}async getIconSource(){let o=_e(this.library),e=this.family||li();if(this.name&&o){let t=this.canvas==="auto"||this.autoWidth,i;try{i=await o.resolver(this.name,e,this.variant,t)}catch{i=void 0}return{url:i,fromLibrary:!0}}return{url:this.src,fromLibrary:!1}}handleLabelChange(){typeof this.label=="string"&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){let{url:o,fromLibrary:e}=await this.getIconSource(),t=e?_e(this.library):void 0;if(!o){this.svg=null;return}let i=Ge.get(o);i||(i=this.resolveIcon(o,t),Ge.set(o,i));let r=await i;r===Ee&&Ge.delete(o);let a=await this.getIconSource();if(o===a.url){if(St(r)){this.svg=r;return}switch(r){case Ee:case ce:this.svg=null,this.dispatchEvent(new ze);break;default:this.svg=r.cloneNode(!0),t?.mutator?.(this.svg,this),this.dispatchEvent(new Ae)}}}willUpdate(o){return this.style||this.setStyleProperty("--rotate-angle",`${this.rotate}deg`),super.willUpdate(o)}updated(o){super.updated(o);let e=_e(this.library);this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`);let t=this.shadowRoot?.querySelector("svg");t&&e?.mutator?.(t,this)}render(){return this.hasUpdated?this.svg:h`<svg part="svg" width="16" height="16" viewBox="0 0 16 16"></svg>`}};w.css=ei;b([re()],w.prototype,"svg",2);b([d({reflect:!0})],w.prototype,"name",2);b([d({reflect:!0})],w.prototype,"family",2);b([d({reflect:!0})],w.prototype,"variant",2);b([d({reflect:!0})],w.prototype,"canvas",2);b([d({attribute:"auto-width",type:Boolean,reflect:!0})],w.prototype,"autoWidth",2);b([d({attribute:"swap-opacity",type:Boolean,reflect:!0})],w.prototype,"swapOpacity",2);b([d()],w.prototype,"src",2);b([d()],w.prototype,"label",2);b([d({reflect:!0})],w.prototype,"library",2);b([d({type:Number,reflect:!0})],w.prototype,"rotate",2);b([d({type:String,reflect:!0})],w.prototype,"flip",2);b([d({type:String,reflect:!0})],w.prototype,"animation",2);b([F("label")],w.prototype,"handleLabelChange",1);b([F(["family","name","library","variant","src","autoWidth","canvas","swapOpacity"],{waitUntilFirstUpdate:!0})],w.prototype,"setIcon",1);w=b([M("wa-icon")],w);var di=g`:host {
  --track-width: 2px;
  --track-color: var(--wa-color-neutral-fill-normal);
  --indicator-color: var(--wa-color-brand-fill-loud);
  --speed: 2s;
  --size: 1em;
  flex: none;
  display: inline-flex;
  width: var(--size);
  height: var(--size);
}
svg {
  width: 100%;
  height: 100%;
  aspect-ratio: 1;
  animation: spin var(--speed) linear infinite;
}
.track,
.indicator {
  --radius: calc(var(--size) / 2 - var(--track-width) / 2);
  --circumference: calc(var(--radius) * 2 * 3.141592654);
  cx: calc(var(--size) / 2);
  cy: calc(var(--size) / 2);
  r: var(--radius);
  fill: none;
  stroke-width: var(--track-width);
}
.track {
  stroke: var(--track-color);
}
.indicator {
  stroke: var(--indicator-color);
  stroke-linecap: round;
  stroke-dasharray: calc(0.597 * var(--circumference)), calc(0.796 * var(--circumference));
  stroke-dashoffset: calc(-0.04 * var(--circumference));
  animation: dash 1.5s ease-in-out infinite;
}
@media (prefers-reduced-motion: reduce) {
  svg,
  .indicator {
    animation: none;
  }
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes dash {
  0% {
    stroke-dasharray: calc(0.008 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: calc(0.716 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: calc(-0.278 * var(--circumference));
  }
  100% {
    stroke-dasharray: calc(0.716 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: calc(-0.987 * var(--circumference));
  }
}
`;var Gi=Object.defineProperty,Ji=Object.getOwnPropertyDescriptor,Zi=(o,e,t,i)=>{for(var r=i>1?void 0:i?Ji(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&Gi(e,t,r),r},Je=class extends ${constructor(){super(...arguments),this.localize=new K(this)}render(){return h`
      <svg
        part="base spinner"
        role="progressbar"
        aria-label=${this.localize.term("loading")}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle class="track" />
        <circle class="indicator" />
      </svg>
    `}};Je.css=di;Je=Zi([M("wa-spinner")],Je);var hi=g`@layer wa-component {
  :host {
    display: inline-block;
  }
  :host:has(wa-badge) {
    position: relative;
  }
  :host(:has(wa-badge)) {
    position: relative;
  }
}
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  white-space: nowrap;
  vertical-align: middle;
  transition-property:
    background,
    border,
    box-shadow,
    color,
    opacity,
    transform;
  transition-duration: var(--wa-transition-fast);
  transition-timing-function: var(--wa-transition-easing);
  transform-origin: center;
  cursor: pointer;
  padding: 0 var(--wa-form-control-padding-inline);
  font-family: inherit;
  font-size: inherit;
  font-weight: var(--wa-font-weight-action);
  height: var(--wa-form-control-height);
  width: 100%;
  background-color: var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud));
  border-color: transparent;
  color: var(--wa-color-on-loud, var(--wa-color-neutral-on-loud));
  border-start-start-radius: var(--_button-start-start-radius, var(--wa-form-control-border-radius));
  border-start-end-radius: var(--_button-start-end-radius, var(--wa-form-control-border-radius));
  border-end-start-radius: var(--_button-end-start-radius, var(--wa-form-control-border-radius));
  border-end-end-radius: var(--_button-end-end-radius, var(--wa-form-control-border-radius));
  border-style: var(--wa-form-control-border-style);
  border-width: var(--wa-form-control-border-width);
}
@media (hover: hover) {
  .button:not(.disabled):not(.loading):hover {
    transform: var(--wa-button-transform-hover);
  }
}
.button:not(.disabled):not(.loading):active {
  transform: var(--wa-button-transform-active);
}
@media (prefers-reduced-motion: reduce) {
  .button:not(.disabled):not(.loading):hover,
  .button:not(.disabled):not(.loading):active {
    transform: none;
  }
}
:host([appearance="plain"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="plain"]) .button {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: transparent;
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="plain"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
    background-color: var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet));
  }
}
:host([appearance="plain"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: color-mix(in oklab, var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet)), var(--wa-color-mix-active));
}
:host([appearance="outlined"]) {
  margin-inline-start: var(--_button-horizontal-indent-outlined);
  margin-block-start: var(--_button-vertical-indent-outlined);
}
:host([appearance="outlined"]) .button {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: transparent;
  border-color: var(--wa-color-border-loud, var(--wa-color-neutral-border-loud));
}
@media (hover: hover) {
  :host([appearance="outlined"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
    background-color: var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet));
  }
}
:host([appearance="outlined"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: color-mix(in oklab, var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet)), var(--wa-color-mix-active));
}
:host([appearance="filled"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="filled"]) .button {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal));
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="filled"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
    background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-hover));
  }
}
:host([appearance="filled"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-active));
}
:host([appearance="filled-outlined"]) {
  margin-inline-start: var(--_button-horizontal-indent-outlined);
  margin-block-start: var(--_button-vertical-indent-outlined);
}
:host([appearance="filled-outlined"]) .button {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal));
  border-color: var(--wa-color-border-normal, var(--wa-color-neutral-border-normal));
}
@media (hover: hover) {
  :host([appearance="filled-outlined"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
    background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-hover));
  }
}
:host([appearance="filled-outlined"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-active));
}
:host([appearance="accent"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="accent"]) .button {
  color: var(--wa-color-on-loud, var(--wa-color-neutral-on-loud));
  background-color: var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud));
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="accent"]) .button:not(.disabled):not(.loading):hover {
    background-color: color-mix(in oklab, var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud)), var(--wa-color-mix-hover));
  }
}
:host([appearance="accent"]) .button:not(.disabled):not(.loading):active {
  background-color: color-mix(in oklab, var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud)), var(--wa-color-mix-active));
}
.button:focus {
  outline: none;
}
.button:focus-visible {
  outline: var(--wa-focus-ring);
  outline-offset: var(--wa-focus-ring-offset);
}
:host([disabled]) {
  opacity: 0.5;
  cursor: not-allowed;
}
:host([disabled]) .button {
  pointer-events: none;
}
.button::-moz-focus-inner {
  border: 0;
}
.button.is-icon-button {
  outline-offset: 2px;
  width: var(--wa-form-control-height);
  aspect-ratio: 1;
}
.button.is-icon-button.caret {
  width: auto;
  aspect-ratio: auto;
  min-width: var(--wa-form-control-height);
}
:host([pill]) .button {
  border-start-start-radius: var(--_button-start-start-radius, var(--wa-border-radius-pill));
  border-start-end-radius: var(--_button-start-end-radius, var(--wa-border-radius-pill));
  border-end-start-radius: var(--_button-end-start-radius, var(--wa-border-radius-pill));
  border-end-end-radius: var(--_button-end-end-radius, var(--wa-border-radius-pill));
}
.start,
.end {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  pointer-events: none;
}
.label {
  display: inline-block;
}
.is-icon-button .label {
  display: flex;
  justify-content: center;
}
.label::slotted(wa-icon) {
  align-self: center;
}
wa-icon[part=caret] {
  display: flex;
  align-self: center;
  align-items: center;
}
wa-icon[part=caret]::part(svg) {
  width: 0.875em;
  height: 0.875em;
}
.button:has(wa-icon[part=caret]) .end {
  display: none;
}
.loading {
  position: relative;
  cursor: wait;
}
.loading .start,
.loading .label,
.loading .end,
.loading .caret {
  opacity: 0;
  pointer-events: none;
}
.loading wa-spinner {
  --indicator-color: currentColor;
  --track-color: color-mix(in oklab, currentColor, transparent 90%);
  position: absolute;
  font-size: 1em;
  height: 1em;
  width: 1em;
  top: calc(50% - 0.5em);
  left: calc(50% - 0.5em);
}
.button ::slotted(wa-badge) {
  border-color: var(--wa-color-surface-default);
  position: absolute;
  inset-block-start: 0;
  inset-inline-end: 0;
  translate: 50% -50%;
  pointer-events: none;
}
:host(:dir(rtl)) ::slotted(wa-badge) {
  translate: -50% -50%;
}
slot[name=start]::slotted(*) {
  margin-inline-end: 0.75em;
}
slot[name=end]::slotted(*),
.button:not(.visually-hidden-label) [part=caret] {
  margin-inline-start: 0.75em;
}
`;var Qi=Object.defineProperty,eo=Object.getOwnPropertyDescriptor,p=(o,e,t,i)=>{for(var r=i>1?void 0:i?eo(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&Qi(e,t,r),r},m=class extends z{constructor(){super(...arguments),this.assumeInteractionOn=["click"],this.hasSlotController=new W(this,"[default]","start","end"),this.localize=new K(this),this.invalid=!1,this.isIconButton=!1,this.title="",this.accessibleLabel="",this.ariaLabel=null,this.variant="neutral",this.appearance="accent",this.size="m",this.withCaret=!1,this.withStart=!1,this.withEnd=!1,this.disabled=!1,this.loading=!1,this.pill=!1,this.type="button",this.iconTag="wa-icon"}static get validators(){return[...super.validators,Ht()]}handleSizeChange(){Nt(this.localName,this.size)}constructLightDOMButton(){let o=document.createElement("button");for(let e of this.attributes)e.name!=="style"&&o.setAttribute(e.name,e.value);return o.type=this.type,o.style.position="absolute !important",o.style.width="0 !important",o.style.height="0 !important",o.style.clipPath="inset(50%) !important",o.style.overflow="hidden !important",o.style.whiteSpace="nowrap !important",this.name&&(o.name=this.name),o.value=this.value||"",o}handleClick(o){if(this.disabled||this.loading){o.preventDefault(),o.stopImmediatePropagation();return}if(this.type!=="submit"&&this.type!=="reset"||!this.getForm())return;let t=this.constructLightDOMButton();this.parentElement?.append(t),t.click(),t.remove()}handleInvalid(){this.dispatchEvent(new j)}handleLabelSlotChange(){let o=this.labelSlot.assignedNodes({flatten:!0}),e=!1,t=!1,i=!1,r=!1,a=this.iconTag==="wa-icon";[...o].forEach(s=>{if(s.nodeType===Node.ELEMENT_NODE){let n=s;s.localName===this.iconTag&&(t=!0,e||(e=s.hasAttribute(a?"label":"aria-label"))),n.localName==="wa-icon"?(t=!0,e||(e=n.label!==void 0)):r=!0}else s.nodeType===Node.TEXT_NODE&&(s.textContent?.trim()||"").length>0&&(i=!0)}),this.isIconButton=t&&!i&&!r,this.customStates.set("icon-button",this.isIconButton),this.isIconButton&&!e&&!this.accessibleLabel&&!this.ariaLabel&&console.warn(`Icon buttons must have a label for screen readers. Add <${this.iconTag} ${a?"label":"aria-label"}="..."> to remove this warning.`,this)}isButton(){return!this.href}isLink(){return!!this.href}handleDisabledChange(){this.customStates.set("disabled",this.disabled),this.updateValidity()}handleHrefChange(){this.customStates.set("link",this.isLink())}handleLoadingChange(){this.customStates.set("loading",this.loading)}setValue(...o){}click(){this.button.click()}focus(o){this.button.focus(o)}blur(){this.button.blur()}render(){let o=this.isLink(),e=o?qe`a`:qe`button`;return Ce`
      <${e}
        part="base button"
        class=${ae({button:!0,caret:this.withCaret,disabled:this.disabled,loading:this.loading,rtl:this.localize.dir()==="rtl","has-label":this.hasSlotController.test("[default]"),"has-start":this.hasSlotController.test("start","withStart"),"has-end":this.hasSlotController.test("end","withEnd"),"is-icon-button":this.isIconButton})}
        ?disabled=${S(o?void 0:this.disabled)}
        type=${S(o?void 0:this.type)}
        title=${this.title}
        name=${S(o?void 0:this.name)}
        value=${S(o?void 0:this.value)}
        href=${S(o?this.href:void 0)}
        target=${S(o?this.target:void 0)}
        download=${S(o?this.download:void 0)}
        rel=${S(o&&this.rel?this.rel:void 0)}
        role=${S(o?void 0:"button")}
        aria-disabled=${S(o&&this.disabled?"true":void 0)}
        aria-label=${S(this.accessibleLabel||this.ariaLabel||void 0)}
        aria-busy=${this.loading?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @invalid=${this.isButton()?this.handleInvalid:null}
        @click=${this.handleClick}
      >
        <slot name="start" part="start" class="start"></slot>
        <slot part="label" class="label" @slotchange=${this.handleLabelSlotChange}></slot>
        <slot name="end" part="end" class="end"></slot>
        ${this.withCaret?Ce`
                <wa-icon part="caret" class="caret" library="system" name="chevron-down" variant="solid"></wa-icon>
              `:""}
        ${this.loading?Ce`<wa-spinner part="spinner"></wa-spinner>`:""}
      </${e}>
    `}};m.shadowRootOptions={...z.shadowRootOptions,delegatesFocus:!0};m.css=[hi,Kt,$e];p([Ve(".button")],m.prototype,"button",2);p([Ve("slot:not([name])")],m.prototype,"labelSlot",2);p([re()],m.prototype,"invalid",2);p([re()],m.prototype,"isIconButton",2);p([d()],m.prototype,"title",2);p([d({attribute:"accessible-label"})],m.prototype,"accessibleLabel",2);p([d({attribute:"aria-label"})],m.prototype,"ariaLabel",2);p([d({reflect:!0})],m.prototype,"variant",2);p([d({reflect:!0})],m.prototype,"appearance",2);p([d({reflect:!0})],m.prototype,"size",2);p([F("size")],m.prototype,"handleSizeChange",1);p([d({attribute:"with-caret",type:Boolean,reflect:!0})],m.prototype,"withCaret",2);p([d({attribute:"with-start",type:Boolean})],m.prototype,"withStart",2);p([d({attribute:"with-end",type:Boolean})],m.prototype,"withEnd",2);p([d({type:Boolean})],m.prototype,"disabled",2);p([d({type:Boolean,reflect:!0})],m.prototype,"loading",2);p([d({type:Boolean,reflect:!0})],m.prototype,"pill",2);p([d()],m.prototype,"type",2);p([d({reflect:!0})],m.prototype,"name",2);p([d({reflect:!0})],m.prototype,"value",2);p([d({reflect:!0})],m.prototype,"href",2);p([d()],m.prototype,"target",2);p([d()],m.prototype,"rel",2);p([d()],m.prototype,"download",2);p([d({attribute:"formaction"})],m.prototype,"formAction",2);p([d({attribute:"formenctype"})],m.prototype,"formEnctype",2);p([d({attribute:"formmethod"})],m.prototype,"formMethod",2);p([d({attribute:"formnovalidate",type:Boolean})],m.prototype,"formNoValidate",2);p([d({attribute:"formtarget"})],m.prototype,"formTarget",2);p([d()],m.prototype,"iconTag",2);p([F("disabled",{waitUntilFirstUpdate:!0})],m.prototype,"handleDisabledChange",1);p([F("href")],m.prototype,"handleHrefChange",1);p([F("loading",{waitUntilFirstUpdate:!0})],m.prototype,"handleLoadingChange",1);m=p([M("wa-button")],m);m.disableWarning?.("change-in-update");var Ze=class extends m{constructor(){super(...arguments);this.appearance="outlined";this.pressed=void 0;this.busy=!1}static{this.properties={pressed:{type:Boolean},busy:{type:Boolean,reflect:!0}}}updated(t){super.updated(t),this.pressed===void 0?this.button.removeAttribute("aria-pressed"):this.button.setAttribute("aria-pressed",String(this.pressed)),this.busy?this.button.setAttribute("aria-busy","true"):this.button.removeAttribute("aria-busy")}render(){return h`
      ${super.render()}
      ${this.busy?h`<svg class="busy-outline" aria-hidden="true">
              <rect pathLength="100"></rect>
            </svg>`:u}
    `}static get styles(){return[m.styles,g`
        :host {
          position: relative;
          --wa-form-control-height: var(--axis-control-height);
          --wa-form-control-padding-inline: var(--axis-space-3);
          --wa-form-control-border-radius: var(--axis-radius-control);
          --wa-form-control-border-width: var(--axis-border-width);
          --wa-form-control-border-style: solid;
          --wa-font-weight-action: var(--axis-font-weight-medium);
          --wa-button-transform-hover: none;
          --wa-button-transform-active: none;
        }
        .button {
          min-block-size: var(--axis-control-height);
          block-size: auto;
          padding-block: var(--axis-space-2);
          white-space: normal;
          overflow-wrap: anywhere;
        }
        :host([busy]) .button {
          border-color: transparent;
        }
        .busy-outline {
          position: absolute;
          inset: 0;
          inline-size: 100%;
          block-size: 100%;
          pointer-events: none;
        }
        .busy-outline rect {
          x: 1px;
          y: 1px;
          width: calc(100% - 2px);
          height: calc(100% - 2px);
          rx: var(--axis-radius-control);
          fill: none;
          stroke: var(--axis-color-primary);
          stroke-width: 2px;
          stroke-dasharray: 3 2;
          animation: busy-dashes 650ms linear infinite;
        }
        @keyframes busy-dashes {
          to {
            stroke-dashoffset: -5;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .busy-outline rect {
            animation: none;
          }
        }
      `]}};customElements.define("axis-button",Ze);var ui=g`:host {
  --spacing: var(--wa-space-l);
  --inner-border-radius: calc(var(--wa-panel-border-radius) - var(--wa-panel-border-width));
  display: flex;
  flex-direction: column;
  background-color: var(--wa-color-surface-default);
  border-color: var(--wa-color-surface-border);
  border-radius: var(--wa-panel-border-radius);
  border-style: var(--wa-panel-border-style);
  box-shadow: var(--wa-shadow-s);
  border-width: var(--wa-panel-border-width);
  color: var(--wa-color-text-normal);
}
:host([appearance="plain"]) {
  background-color: transparent;
  border-color: transparent;
  box-shadow: none;
}
:host([appearance="outlined"]) {
  background-color: var(--wa-color-surface-default);
  border-color: var(--wa-color-surface-border);
}
:host([appearance="filled"]) {
  background-color: var(--wa-color-neutral-fill-quiet);
  border-color: transparent;
}
:host([appearance="filled-outlined"]) {
  background-color: var(--wa-color-neutral-fill-quiet);
  border-color: var(--wa-color-surface-border);
}
:host([appearance="accent"]) {
  color: var(--wa-color-neutral-on-loud);
  background-color: var(--wa-color-neutral-fill-loud);
  border-color: transparent;
}
.media,
:host(:not([with-media])) .header,
:host(:not([with-media], [with-header])) .body {
  border-start-start-radius: var(--inner-border-radius);
  border-start-end-radius: var(--inner-border-radius);
}
:host(:not([with-footer])) .body,
.footer {
  border-end-start-radius: var(--inner-border-radius);
  border-end-end-radius: var(--inner-border-radius);
}
.media {
  display: flex;
  overflow: hidden;
}
.media::slotted(*) {
  display: block;
  width: 100%;
  border-radius: 0 !important;
}
:host([appearance="plain"]) .media {
  border-radius: var(--inner-border-radius);
}
:host([appearance="plain"]) .media::slotted(*) {
  border-radius: inherit !important;
}
.header {
  display: block;
  border-block-end-style: inherit;
  border-block-end-color: var(--wa-color-surface-border);
  border-block-end-width: var(--wa-panel-border-width);
  padding: calc(var(--spacing) / 2) var(--spacing);
}
.body {
  display: block;
  padding: var(--spacing);
}
.footer {
  display: block;
  border-block-start-style: inherit;
  border-block-start-color: var(--wa-color-surface-border);
  border-block-start-width: var(--wa-panel-border-width);
  padding: var(--spacing);
}
.has-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
:host(:not([with-header])) .header,
:host(:not([with-footer])) .footer,
:host(:not([with-media])) .media {
  display: none;
}
:host([orientation="horizontal"]) {
  flex-direction: row;
}
:host([orientation="horizontal"]) .media {
  border-start-start-radius: var(--inner-border-radius);
  border-end-start-radius: var(--inner-border-radius);
  border-start-end-radius: 0;
}
:host([orientation="horizontal"]) .media::slotted(*) {
  block-size: 100%;
  inline-size: 100%;
  object-fit: cover;
}
:host([orientation="horizontal"]) .body slot::slotted(*) {
  display: block;
  height: 100%;
  margin: 0;
}
:host([orientation="horizontal"]) slot[name=actions]::slotted(*) {
  display: flex;
  align-items: center;
  padding: var(--spacing);
}
`;var to=Object.defineProperty,io=Object.getOwnPropertyDescriptor,T=(o,e,t,i)=>{for(var r=i>1?void 0:i?io(e,t):e,a=o.length-1,s;a>=0;a--)(s=o[a])&&(r=(i?s(e,t,r):s(r))||r);return i&&r&&to(e,t,r),r},L=class extends ${constructor(){super(...arguments),this.hasSlotController=new W(this,"footer","header","media","header-actions","footer-actions","actions"),this.appearance="outlined",this.withHeader=!1,this.withMedia=!1,this.withFooter=!1,this.withHeaderActions=!1,this.withFooterActions=!1,this.orientation="vertical"}willUpdate(o){this.withHeader=this.hasSlotController.test("header","withHeader"),this.withMedia=this.hasSlotController.test("media","withMedia"),this.withFooter=this.hasSlotController.test("footer","withFooter"),super.willUpdate(o)}render(){if(this.orientation==="horizontal")return h`
        <slot name="media" part="media" class="media"></slot>
        <div part="body" class="body"><slot></slot></div>
        <slot name="actions" part="actions" class="actions"></slot>
      `;let o=this.hasSlotController.test("header-actions","withHeaderActions"),e=this.hasSlotController.test("footer-actions","withFooterActions");return h`
      <slot name="media" part="media" class="media"></slot>

      <div
        part="header"
        class=${ae({header:!0,"has-actions":o})}
      >
        <slot name="header"></slot>
        <slot name="header-actions"></slot>
      </div>

      <div part="body" class="body"><slot></slot></div>

      <div
        part="footer"
        class=${ae({footer:!0,"has-actions":e})}
      >
        <slot name="footer"></slot>
        <slot name="footer-actions"></slot>
      </div>
    `}};L.css=[$e,ui];T([d({reflect:!0})],L.prototype,"appearance",2);T([d({attribute:"with-header",type:Boolean,reflect:!0})],L.prototype,"withHeader",2);T([d({attribute:"with-media",type:Boolean,reflect:!0})],L.prototype,"withMedia",2);T([d({attribute:"with-footer",type:Boolean,reflect:!0})],L.prototype,"withFooter",2);T([d({attribute:"with-header-actions",type:Boolean,reflect:!0})],L.prototype,"withHeaderActions",2);T([d({attribute:"with-footer-actions",type:Boolean,reflect:!0})],L.prototype,"withFooterActions",2);T([d({reflect:!0})],L.prototype,"orientation",2);L=T([M("wa-card")],L);L.disableWarning?.("change-in-update");var Qe=class extends L{static get styles(){return[L.styles,g`
        :host {
          --spacing: var(--axis-space-4);
          --wa-panel-border-radius: var(--axis-radius-card);
          --wa-panel-border-width: var(--axis-border-width);
          --wa-panel-border-style: solid;
          --wa-shadow-s: none;
          min-inline-size: 0;
        }
      `]}};customElements.define("axis-card",Qe);var et=class extends x{constructor(){super(...arguments);this.device=null;this.health=null;this.loading=!1}static{this.properties={device:{attribute:!1},health:{attribute:!1},loading:{type:Boolean}}}static{this.styles=U}render(){if(!this.device)return u;let t=this.health?.serial===this.device.serial;return h`
      <axis-card>
        <h3>Device health</h3>
        ${!this.loading&&!this.health?h`<p>No live health data available. Check the connection and select Health again to retry.</p>`:u}
        ${this.health?h`
                ${t?u:h`<p class="warning">Warning: the connected device serial does not match the saved target.</p>`}
                <dl>
                  ${t?h`<dt>Serial</dt>
                          <dd>${this.health.serial}</dd>`:h`<dt>Saved serial</dt>
                          <dd>${this.device.serial}</dd>
                          <dt>Reported serial</dt>
                          <dd>${this.health.serial}</dd>`}
                  <dt>Product</dt>
                  <dd>${this.health.product}</dd>
                  <dt>Model</dt>
                  <dd>${this.health.model}</dd>
                  <dt>Firmware</dt>
                  <dd>${this.health.firmware_version}</dd>
                  <dt>Read at</dt>
                  <dd>${this.health.observed_at}</dd>
                </dl>
              `:u}
      </axis-card>
    `}};customElements.define("axis-device-health",et);function q(o){let e=o?.trim().toLowerCase().replace(/\*+$/,"").replace(/[:-]/g,"");return e&&/^[0-9a-f]{12}$/.test(e)?e:void 0}function mi(o,e,t,i,r=!1){let a=[o?e:"",t,i].filter(Boolean).join(" \u2014 ");return h`
    <span class="device-info">
      <span class="device-heading">
        <span class="device-name">${o||e}</span>
        ${r?h`<span class="warning">Discovered</span>`:u}
      </span>
      ${a?h`<span class="device-meta">${a}</span>`:u}
    </span>
  `}function oo(o,e){let t=q(o.macaddress);return e.some(i=>i.serial===o.serial||t!==void 0&&(t===q(i.serial)||t===q(i.discovery?.macaddress)))}var tt=class extends x{constructor(){super(...arguments);this.devices=[];this.discovery=null;this.selected="";this.connected=!1}static{this.properties={devices:{attribute:!1},discovery:{attribute:!1},selected:{},connected:{type:Boolean}}}static{this.styles=[U,g`
      .device-rows {
        display: grid;
        gap: var(--axis-space-2);
        list-style: none;
        margin-block: var(--axis-space-2) 0;
        padding: 0;
      }
      .device-rows li {
        min-inline-size: 0;
      }
      .device-rows axis-button {
        display: block;
        inline-size: 100%;
      }
      .device-rows axis-button::part(base) {
        justify-content: flex-start;
        text-align: start;
      }
      .device-info {
        display: grid;
        gap: var(--axis-space-1);
        min-inline-size: 0;
      }
      .device-heading {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        gap: var(--axis-space-2);
      }
      .device-meta {
        font-size: 0.875rem;
        font-weight: 400;
        opacity: 0.9;
      }
      .device-heading .warning {
        font-size: 0.75rem;
      }
      .discovered {
        --wa-color-neutral-border-quiet: var(--axis-color-warning);
      }
      .discovered::part(base) {
        border-color: var(--axis-color-warning);
      }
      .scan-control {
        position: relative;
        display: flex;
        justify-content: flex-end;
        margin-block-start: var(--axis-space-2);
      }
      .scan-control .failed::part(base) {
        border-color: var(--axis-color-danger);
      }
      .scan-status {
        position: absolute;
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        clip-path: inset(50%);
        white-space: nowrap;
      }
    `]}render(){let t=this.discovery,i=t?.devices??[],r=i.filter(l=>!oo(l,this.devices)),a=t?.status==="scanning",s=t?.status==="error",n=a?"Discovering devices\u2026":s?"Retry discovery \xB7 Failed":t?.status==="complete"?`Discover devices \xB7 ${r.length?`${r.length} new`:"No new devices"}`:"Discover devices",c=s?t.message:t?.status==="complete"&&!r.length?i.length?"All discovered devices are already saved.":"No Axis devices found.":t?n:"";return h`
      <axis-card>
        ${this.devices.length||r.length?h`
                <ul class="device-rows" role="list" aria-label="Devices">
                  ${this.devices.map(l=>h`
                      <li>
                        <axis-button
                          variant=${l.serial===this.selected?"brand":"neutral"}
                          appearance=${l.serial===this.selected?"accent":"outlined"}
                          .pressed=${l.serial===this.selected}
                          ?disabled=${!this.connected}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-select",{detail:l.serial}))}
                        >
                          ${mi(oe(l),l.host,l.discovery?.macaddress||q(l.serial)?.match(/../g)?.join(":"))}
                        </axis-button>
                      </li>
                    `)}
                  ${r.map(l=>h`
                      <li>
                        <axis-button
                          class="discovered"
                          ?disabled=${!this.connected}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-register",{detail:l}))}
                        >
                          ${mi(l.name,l.host,l.macaddress,l.model,!0)}
                        </axis-button>
                      </li>
                    `)}
                </ul>
              `:u}
        <div class="scan-control">
          <axis-button
            class=${s?"failed":""}
            .busy=${a}
            ?disabled=${!this.connected}
            aria-disabled=${a?"true":"false"}
            title=${s?t.message:""}
            @click=${()=>{this.connected&&!a&&this.dispatchEvent(new Event("axis-scan"))}}
            >${n}</axis-button
          >
          <span class="scan-status" role="status">${c}</span>
        </div>
        ${this.devices.length===0?h`<p>No saved devices. Use Discover devices to find devices on the local network.</p>`:""}
      </axis-card>
    `}};customElements.define("axis-device-list",tt);var ro=["Health","APIs","Interfaces"],ao={connecting:"Connecting to Axis\u2026",connected:"Connected to Axis",reconnecting:"Reconnecting to Axis\u2026",denied:"Access link rejected","link-required":"Access link required"},it=o=>o==="https"?443:80;function so(o,e){let t=Number(o.get("port")),i=String(o.get("web_proto")??"");return e?.web_proto===i&&e.port===t?t:t===it(i)?0:t}function ke(o,e){let t=i=>String(o.get(i)??"");return{host:t("host"),port:so(o,e),username:t("username"),password:t("password"),web_proto:t("web_proto"),verify_ssl:o.has("verify_ssl")}}var ot=class extends x{constructor(){super(...arguments);this.status="connecting";this.devices=[];this.discovery=null;this.selected="";this.deviceView="Health";this.viewData={};this.selectedInterface=null;this.error="";this.loading=null;this.registration=null;this.saving=!1;this.saveError="";this.settings=null;this.settingsPending=!1;this.settingsError="";this.connectionEdited=!1;this.connectionTest=null;this.operation=0;this.refreshId=0;this.backdropPressed=!1;this.portDrafts=new WeakMap;this.connection=new ye(t=>this.connectionChanged(t));this.openAccessLink=()=>{let t=location.hash.slice(1)||sessionStorage.getItem("axis-token")||"";if(location.hash&&(sessionStorage.setItem("axis-token",t),history.replaceState(null,"",location.pathname)),!t){this.connection.disconnect(),this.status="link-required",this.error="Open the private URL printed when the server starts.";return}this.connection.connect(t)};this.alignDeviceDialog=()=>{let t=this.renderRoot.querySelector("dialog"),i=this.renderRoot.querySelector("axis-device-list");if(t&&i){let r=i.getBoundingClientRect().top+window.scrollY;t.style.setProperty("--axis-dialog-top",`${r}px`)}}}static{this.properties={status:{state:!0},devices:{state:!0},discovery:{state:!0},selected:{state:!0},deviceView:{state:!0},viewData:{state:!0},selectedInterface:{state:!0},error:{state:!0},loading:{state:!0},registration:{state:!0},saving:{state:!0},saveError:{state:!0},settings:{state:!0},settingsPending:{state:!0},settingsError:{state:!0},connectionEdited:{state:!0},connectionTest:{state:!0}}}static{this.styles=[U,g`
      main {
        max-inline-size: var(--axis-content-width);
        margin-inline: auto;
        padding: var(--axis-space-6);
      }
      header {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: baseline;
        gap: var(--axis-space-4);
      }
      .app-heading {
        display: block;
        margin-block-end: var(--axis-space-4);
      }
      .app-heading h1 {
        margin-block-end: 0;
      }
      .connection-heading {
        display: inline-block;
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .connection-status {
        display: block;
        block-size: 3px;
        margin-block-start: var(--axis-space-1);
        border-radius: var(--axis-radius-control);
        background-color: var(--axis-color-danger);
      }
      .connection-status[data-state="connected"] {
        background-color: var(--axis-color-success);
      }
      .connection-status:is(
        [data-state="connecting"],
        [data-state="reconnecting"]
      ) {
        background-color: light-dark(#a94c00, #ffd08a);
        animation: connection-pulse 1.6s ease-in-out infinite alternate;
      }
      @keyframes connection-pulse {
        to {
          opacity: 0.55;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .connection-status:is(
          [data-state="connecting"],
          [data-state="reconnecting"]
        ) {
          animation: none;
        }
      }
      .panels {
        display: grid;
        gap: var(--axis-space-4);
      }
      dialog {
        box-sizing: border-box;
        inline-size: min(
          var(--axis-content-width),
          calc(100% - var(--axis-space-4))
        );
        max-inline-size: none;
        inset-block: var(--axis-dialog-top) auto;
        margin-block: 0;
        max-block-size: calc(
          100dvh - var(--axis-dialog-top) - var(--axis-space-2)
        );
        padding: 0;
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-card);
        background: var(--axis-color-background);
        color: var(--axis-color-text);
        overflow: hidden;
      }
      dialog[open] {
        display: grid;
        grid-template-rows: auto minmax(0, 1fr);
      }
      dialog::backdrop {
        background: rgb(0 0 0 / 55%);
      }
      .dialog-header {
        padding: var(--axis-space-4);
        border-block-end: var(--axis-border-width) solid
          var(--axis-color-border);
      }
      .dialog-heading {
        flex-wrap: nowrap;
        align-items: start;
      }
      .dialog-header h2 {
        margin: 0;
        min-inline-size: 0;
        overflow-wrap: anywhere;
      }
      .dialog-controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: var(--axis-space-2);
      }
      .device-views axis-button::part(base) {
        border-color: transparent;
        background: transparent;
      }
      .device-views axis-button.active::part(base) {
        border-color: var(--axis-color-border);
        background: var(--axis-color-surface-muted);
        color: var(--axis-color-primary);
      }
      .settings-form input::placeholder {
        color: color-mix(
          in srgb,
          var(--axis-color-text) 70%,
          var(--axis-color-surface)
        );
        opacity: 1;
      }
      .settings-form fieldset + fieldset {
        margin-block-start: var(--axis-space-4);
      }
      .settings-form legend {
        font-weight: var(--axis-font-weight-medium);
        margin-block-end: var(--axis-space-2);
      }
      .dialog-content {
        overflow: auto;
        overscroll-behavior: contain;
        padding: var(--axis-space-4);
      }
      .error {
        color: var(--axis-color-danger);
      }
      fieldset {
        display: grid;
        gap: var(--axis-space-3);
        border: 0;
        padding: 0;
        margin: 0;
        min-inline-size: 0;
      }
      label {
        display: grid;
        gap: var(--axis-space-1);
        max-inline-size: 28rem;
      }
      .certificate {
        display: block;
      }
      input,
      select,
      button {
        font: inherit;
        color: inherit;
      }
      input:not([type="checkbox"]),
      select,
      button {
        min-block-size: var(--axis-control-height);
        padding-inline: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface);
      }
      .form-status,
      .connection-status [role="status"] {
        position: absolute;
        clip-path: inset(50%);
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        white-space: nowrap;
      }
    `]}connectedCallback(){super.connectedCallback(),window.addEventListener("hashchange",this.openAccessLink),window.addEventListener("resize",this.alignDeviceDialog),this.openAccessLink()}disconnectedCallback(){window.removeEventListener("hashchange",this.openAccessLink),window.removeEventListener("resize",this.alignDeviceDialog),this.connection.disconnect(),super.disconnectedCallback()}updated(){let t=this.renderRoot.querySelector("dialog");if(!t)return;this.registration!==null||this.selected!==""?(this.alignDeviceDialog(),t.open||t.showModal()):t.open&&(t.close(),this.shadowRoot?.activeElement||this.renderRoot.querySelector("h1")?.focus())}dismissDevice(t){t?.preventDefault(),!(this.saving||this.settingsPending)&&(++this.operation,this.registration=null,this.settings=null,this.connectionTest=null,this.selected="",this.viewData={},this.selectedInterface=null,this.loading=null,this.error="")}connectionChanged(t){if(!(this.status===t&&t==="reconnecting")){if(this.status=t,this.error=t==="denied"?"Open the private URL printed by the running server.":"",t==="connected"){this.refreshDevices(),this.scanLocalNetwork();return}++this.operation,++this.refreshId,this.discovery&&(this.discovery={status:"interrupted",devices:this.discovery.devices}),this.registration=null,this.settings=null,this.connectionTest=null,this.settingsPending=!1,this.saving=!1,this.saveError="",t!=="reconnecting"&&(this.viewData={},this.selectedInterface=null),this.loading=null}}async refreshDevices(){let t=++this.refreshId;try{let i=await _t(this.connection);if(this.refreshId!==t)return;this.devices=i,this.error="",this.selected&&this.devices.some(r=>r.serial===this.selected)?await this.showDeviceView(this.selected,this.deviceView):(++this.operation,this.selected="",this.viewData={},this.selectedInterface=null,this.loading=null)}catch(i){this.refreshId===t&&(this.error=i.message)}}async scanLocalNetwork(){if(this.status!=="connected"||this.saving||this.discovery?.status==="scanning")return;this.registration=null;let t={status:"scanning",devices:this.discovery?.devices??[]};this.discovery=t;try{let i=await Et(this.connection,r=>{if(this.discovery!==t)return;let a=new Map(t.devices.map(s=>[s.host,s]));a.set(r.host,r),t={status:"scanning",devices:[...a.values()]},this.discovery=t});if(this.discovery===t){let r=new Map(i.map(s=>[s.host,s])),a=t.devices.flatMap(({host:s})=>{let n=r.get(s);return r.delete(s),n?[n]:[]});this.discovery={status:"complete",devices:[...a,...r.values()]}}}catch(i){this.discovery===t&&(this.discovery={status:"error",devices:t.devices,message:i.message})}}openRegistration(t){this.connectionTest=null,this.registration=t,this.saveError="",this.selected="",++this.operation}registrationBlock(t){if(this.discovery?.status==="scanning")return"Wait for discovery to finish before testing the connection.";let i=q(t.macaddress)??t.macaddress;return this.discovery?.status==="complete"&&this.discovery.devices.some(a=>a.host===t.host&&(q(a.macaddress)??a.macaddress)===i)?"":"This device was not confirmed. Close this form and run discovery again."}async submitRegistration(t){t.preventDefault();let i=t.currentTarget,r=this.registration;if(!(i instanceof HTMLFormElement)||!r||this.registrationBlock(r)||this.saving||this.connectionTest?.pending)return;let a=new FormData(i),s=ke(a);if(!this.connectionVerified(s))return;let n=i.querySelector('input[name="password"]');n&&(n.value=""),this.connectionTest=null,this.saving=!0,this.saveError="";try{let c=await kt(this.connection,{...s,host:r.host,alias:String(a.get("alias")??"")});if(this.registration!==r)return;this.registration=null,this.saving=!1,this.selected=c,this.deviceView="Health";let l=this.renderRoot.querySelector(".dialog-content");l&&(l.scrollTop=0),await this.refreshDevices()}catch(c){this.registration===r&&(this.saveError=c.message)}finally{this.registration===r&&(this.saving=!1)}}renderRegistration(t){let i=this.registrationBlock(t);return At(t.host,h`
        <axis-card>
          <h3>Save discovered device</h3>
          <p>
            ${i&&this.discovery?.status!=="scanning"?i:"Enter the device credentials to read its identity and save it locally."}
          </p>
          ${this.renderSettingsForm(t,i)}
        </axis-card>
      `)}async showDeviceView(t,i,r=!1){if(this.deviceView!==i){let a=this.renderRoot.querySelector(".dialog-content");a&&(a.scrollTop=0)}if(this.selected=t,this.deviceView=i,!r&&(i==="Health"&&this.viewData.health||i==="APIs"&&this.viewData.apis||i==="Interfaces"&&this.viewData.interfaces)){this.useCachedView();return}return i==="Health"?this.browse(()=>Ft(this.connection,t),a=>{this.viewData={...this.viewData,health:a}}):i==="APIs"?this.browse(()=>Tt(this.connection,t),a=>{this.viewData={...this.viewData,apis:a}}):this.browse(()=>Pt(this.connection,t),a=>{this.viewData={...this.viewData,interfaces:a},r&&(this.selectedInterface=null)})}async showInterface(t,i){let r=this.selectedInterface===i;if(this.selectedInterface=i,!r&&this.viewData.interfaceResults?.has(i)){this.useCachedView();return}return this.browse(()=>It(this.connection,t,i),a=>{let s=new Map(this.viewData.interfaceResults);s.set(i,a),this.viewData={...this.viewData,interfaceResults:s}},"interface")}useCachedView(){++this.operation,this.loading=null,this.error=""}async browse(t,i,r="view"){let a=++this.operation;this.loading=r,this.error="";try{let s=await t();if(this.operation!==a)return;i(s)}catch(s){this.operation===a&&(this.error=s.message)}finally{this.operation===a&&(this.loading=null)}}renderSavedView(t,i){if(this.deviceView==="Health")return h`
        <axis-device-health
          .device=${t}
          .health=${this.viewData.health??null}
          .loading=${this.loading==="view"}
        ></axis-device-health>
      `;let{apis:r,interfaces:a,interfaceResults:s}=this.viewData,n=this.deviceView==="APIs"?r:this.selectedInterface===null?a:s?.get(this.selectedInterface);return h`
      <axis-card>
        <h3>${this.deviceView}</h3>
        ${this.deviceView==="Interfaces"&&a?.length?h`<div class="actions">
                ${a.map(c=>h`
                    <axis-button
                      .pressed=${this.selectedInterface===c.name}
                      .busy=${this.loading==="interface"&&this.selectedInterface===c.name}
                      ?disabled=${!i||!c.supported}
                      @click=${()=>this.showInterface(t.serial,c.name)}
                    >
                      ${c.name}
                    </axis-button>
                  `)}
              </div>`:u}
        ${n!==void 0?h`<pre>${JSON.stringify(n,null,2)}</pre>`:u}
      </axis-card>
    `}async openSettings(t){this.connectionTest=null,this.connectionEdited=!1;let i={serial:t};this.settingsError="",this.settings=i;try{let r=await Dt(this.connection,t);if(this.settings!==i)return;this.settings={serial:t,value:r},await this.updateComplete,this.renderRoot.querySelector(".settings-form input")?.focus()}catch(r){this.settings===i&&(this.settingsError=r.message)}}async closeSettings(){this.settings=null,this.connectionTest=null,await this.updateComplete,this.renderRoot.querySelector(".settings-trigger")?.focus()}async submitSettings(t){t.preventDefault();let i=this.settings,r=t.currentTarget;if(!i?.value||this.settingsPending||this.connectionTest?.pending||!(r instanceof HTMLFormElement))return;let a=new FormData(r),s=ke(a,i.value.device);if(!(this.needsConnectionTest(s,i.value)&&!this.connectionVerified(s))){this.settingsError="",this.settingsPending=!0;try{let n=await Mt(this.connection,i.serial,{...s,alias:String(a.get("alias")??"")});if(this.settings!==i)return;this.devices=this.devices.map(c=>c.serial===i.serial?n.device:c),this.settingsPending=!1,this.closeSettings(),n.connection_changed&&(this.viewData={},this.selectedInterface=null,this.showDeviceView(i.serial,this.deviceView))}catch(n){this.settings===i&&(this.settingsError=n.message)}finally{this.settings===i&&(this.settingsPending=!1)}}}renderSettings(){let t=this.settings?.value;return h`
      <axis-card>
        <h3>Device settings</h3>
        <p>These settings affect how Axis connects, not the device itself.</p>
        ${!t&&this.settingsError?h`<p class="error" role="alert">${this.settingsError}</p>`:u}
        ${t?this.renderSettingsForm(t):this.settingsError?h`<button type="button" @click=${this.closeSettings}>
                  Back
                </button>`:h`<p role="status">Loading settings…</p>`}
      </axis-card>
    `}async testConnection(t){let i=t.currentTarget,r=i instanceof HTMLElement?i.closest("form"):null;if(!r||this.connectionTest?.pending||!r.reportValidity())return;let a=this.registration,s=this.settings?.value?.device;if(!a&&!s||a&&this.registrationBlock(a))return;let n=ke(new FormData(r),s),c={pending:!0};this.connectionTest=c,this.settingsError="",this.saveError="";try{let l=s?await this.connection.callWS("device/test-connection",{...n,device:s.serial}):await this.connection.callWS("devices/test-connection",n);this.connectionTest===c&&(this.connectionTest={pending:!1,draft:n,message:`Connection successful (serial: ${l}).`})}catch(l){this.connectionTest===c&&(this.connectionTest={pending:!1,failed:!0,message:l.message})}}connectionVerified(t){let i=this.connectionTest?.draft;return i!==void 0&&JSON.stringify(i)===JSON.stringify(t)}needsConnectionTest(t,i){let{device:r,username:a}=i;return t.host.trim()!==r.host||t.port!==r.port||t.web_proto!==r.web_proto||t.verify_ssl!==r.verify_ssl||t.username.trim()!==a||t.password!==""}updateConnectionTest(t){if(this.connectionTest?.pending||!(t.target instanceof HTMLInputElement||t.target instanceof HTMLSelectElement)||t.target.name==="alias"||!(t.currentTarget instanceof HTMLFormElement)||t.type==="input"&&t.target instanceof HTMLSelectElement)return;this.connectionTest=null,this.saveError="",this.settingsError="";let i=this.settings?.value;i&&(this.connectionEdited=this.needsConnectionTest(ke(new FormData(t.currentTarget),i.device),i))}switchPortProtocol(t,i){let r=t.currentTarget;if(!(r instanceof HTMLSelectElement))return;let a=r.form?.elements.namedItem("port");if(!(a instanceof HTMLInputElement))return;let s=this.portDrafts.get(r)??{protocol:i,ports:new Map};s.ports.set(s.protocol,a.value),s.protocol=r.value,a.value=s.ports.get(s.protocol)??String(it(s.protocol)),this.portDrafts.set(r,s)}renderSettingsForm(t,i=""){let r=!("device"in t),a=r?this.saving:this.settingsPending,s=this.connectionTest?.pending??!1,n=r?"Save device":"Save settings",c=this.connectionTest,l=(r||this.connectionEdited)&&!c?.draft,v=r?this.saveError:this.settingsError,f=r?t.name.trim()||t.host:oe({...t.device,alias:""}),y=r?"https":t.device.web_proto,A=(r?0:t.device.port)||it(y);return h`
      <form
        class="settings-form"
        method="post"
        @submit=${r?this.submitRegistration:this.submitSettings}
        @input=${this.updateConnectionTest}
        @change=${this.updateConnectionTest}
        @keydown=${C=>{C.key!=="Enter"||C.isComposing||!(C.target instanceof HTMLInputElement)||C.target.type==="checkbox"||(C.preventDefault(),!a&&!s&&!i&&!l&&C.currentTarget instanceof HTMLFormElement&&C.currentTarget.requestSubmit())}}
      >
        <fieldset ?disabled=${a||s}>
          <legend>General</legend>
          <label>
            Alias
            <input
              name="alias"
              .value=${r?"":t.device.alias}
              placeholder=${f}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${a||s}>
          <legend>Connection</legend>
          <label>
            Address
            <input
              name="host"
              .value=${r?t.host:t.device.host}
              ?readonly=${r}
              required
            />
          </label>
          <label>
            Port
            <input
              name="port"
              type="number"
              min="1"
              max="65535"
              .value=${String(A)}
              required
            />
          </label>
          <label>
            Username
            <input
              name="username"
              autocomplete="username"
              .value=${r?"":t.username}
              required
            />
          </label>
          <label>
            ${r?"Password":"New password"}
            <input
              name="password"
              type="password"
              autocomplete=${r?"current-password":"new-password"}
              placeholder=${r?u:"Keep current password"}
              ?required=${r}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${a||s}>
          <legend>Advanced</legend>
          <label>
            Protocol
            <select
              name="web_proto"
              @change=${C=>this.switchPortProtocol(C,y)}
            >
              <option value="https" ?selected=${y==="https"}>
                HTTPS
              </option>
              <option value="http" ?selected=${y==="http"}>
                HTTP
              </option>
            </select>
          </label>
          <label class="certificate">
            <input
              name="verify_ssl"
              type="checkbox"
              .checked=${!r&&t.device.verify_ssl}
            />
            Verify HTTPS certificates
          </label>
          ${r?h`<small class="warning">
                  Turning verification off allows self-signed certificates but
                  skips certificate checks. HTTP is not encrypted. Verify the
                  address and only continue if you trust the device and network.
                </small>`:h`<small>
                  Use HTTPS with certificate verification when possible. HTTP is
                  not encrypted.
                </small>`}
        </fieldset>
        <div class="actions">
          <axis-button
            type="submit"
            variant=${v?"danger":"brand"}
            .busy=${a}
            ?disabled=${a||s||l||!!i}
            title=${i||v||(l?"Test the connection before saving.":"")}
          >
            ${n}
          </axis-button>
          <axis-button
            type="button"
            variant=${c?.failed?"danger":c?.draft?"success":"neutral"}
            .busy=${s}
            ?disabled=${a||s||!!i}
            title=${i||c?.message||""}
            @click=${this.testConnection}
          >
            Test connection
          </axis-button>
          <axis-button
            type="button"
            ?disabled=${a}
            @click=${r?this.dismissDevice:this.closeSettings}
          >
            Cancel
          </axis-button>
        </div>
        <div class="form-status" role="status">
          ${i||(c?.draft?c.message:"")}
        </div>
        <div class="form-status" role="alert">
          ${v||(c?.failed?c.message:"")}
        </div>
      </form>
    `}renderConnectionStatus(t){return h`
      <span class="connection-status" data-state=${this.status}>
        <span role="status">${t}</span>
      </span>
    `}render(){let t=this.devices.find(n=>n.serial===this.selected),i=this.status==="connected",r=ao[this.status],a=this.registration!==null||this.selected!=="",s=this.error?h`<p class="error" role="alert">${this.error}</p>`:u;return h`
      <main>
        <header class="app-heading">
          <div class="connection-heading" title=${r}>
            <h1 tabindex="-1">Axis devices</h1>
            ${this.renderConnectionStatus(r)}
          </div>
        </header>
        ${a?u:s}
        <axis-device-list
          .devices=${this.devices}
          .discovery=${this.discovery}
          .selected=${this.selected}
          .connected=${i&&!this.saving}
          @axis-scan=${this.scanLocalNetwork}
          @axis-select=${n=>{this.registration=null,this.showDeviceView(n.detail,"Health")}}
          @axis-register=${n=>this.openRegistration(n.detail)}
        >
        </axis-device-list>
      </main>
      <dialog
        aria-labelledby="device-dialog-title"
        @pointerdown=${n=>{let c=n.currentTarget;if(this.backdropPressed=!1,n.target===c&&c instanceof HTMLDialogElement){let l=c.getBoundingClientRect();this.backdropPressed=n.clientX<l.left||n.clientX>=l.right||n.clientY<l.top||n.clientY>=l.bottom}}}
        @pointercancel=${()=>{this.backdropPressed=!1}}
        @click=${n=>{let c=n.currentTarget;if(this.backdropPressed&&n.target===c&&c instanceof HTMLDialogElement){let l=c.getBoundingClientRect();(n.clientX<l.left||n.clientX>=l.right||n.clientY<l.top||n.clientY>=l.bottom)&&this.dismissDevice(n)}this.backdropPressed=!1}}
        @cancel=${n=>{if(!this.settings){this.dismissDevice(n);return}n.preventDefault(),this.settingsPending||this.closeSettings()}}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="device-dialog-title">
              ${this.registration?this.registration.name.trim()||this.registration.host:t?oe(t):"Device details"}
            </h2>
            <div class="dialog-controls">
              ${t?h`<button
                      type="button"
                      class="settings-trigger"
                      aria-pressed=${String(this.settings!==null)}
                      ?disabled=${!i||this.settingsPending}
                      @click=${()=>this.settings?this.closeSettings():this.openSettings(t.serial)}
                    >
                      Settings
                    </button>`:u}
              <button
                type="button"
                autofocus
                ?disabled=${this.saving||this.settingsPending}
                @click=${this.dismissDevice}
              >
                Close
              </button>
            </div>
          </header>
          ${t?h`<nav
                  class="actions device-views"
                  aria-label="Device views"
                >
                  ${ro.map(n=>h`
                      <axis-button
                        class=${!this.settings&&this.deviceView===n?"active":""}
                        variant="neutral"
                        .pressed=${!this.settings&&this.deviceView===n}
                        .busy=${this.loading==="view"&&this.deviceView===n}
                        ?disabled=${!i||this.settingsPending}
                        @click=${()=>{let c=!this.settings&&this.deviceView===n;this.settings=null,this.connectionTest=null,this.showDeviceView(t.serial,n,c)}}
                        >${n}</axis-button
                      >
                    `)}
                </nav>`:u}
        </div>
        <div class="panels dialog-content">
          ${a?s:u}
          ${this.registration?this.renderRegistration(this.registration):u}
          ${this.settings?this.renderSettings():t?this.renderSavedView(t,i):u}
        </div>
      </dialog>
    `}};customElements.define("axis-app",ot);
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
lit-html/directive.js:
@lit/reactive-element/decorators/custom-element.js:
@lit/reactive-element/decorators/property.js:
@lit/reactive-element/decorators/state.js:
@lit/reactive-element/decorators/event-options.js:
@lit/reactive-element/decorators/base.js:
@lit/reactive-element/decorators/query.js:
@lit/reactive-element/decorators/query-all.js:
@lit/reactive-element/decorators/query-async.js:
@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
lit-html/static.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/keyed.js:
@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/class-map.js:
lit-html/directives/if-defined.js:
  (**
   * @license
   * Copyright 2018 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@home-assistant/webawesome/dist/events/invalid.js:
@home-assistant/webawesome/dist/internal/size.js:
@home-assistant/webawesome/dist/internal/slot.js:
@home-assistant/webawesome/dist/internal/validators/mirror-validator.js:
@home-assistant/webawesome/dist/internal/watch.js:
@home-assistant/webawesome/dist/internal/validators/custom-error-validator.js:
@home-assistant/webawesome/dist/styles/component/host.styles.js:
@home-assistant/webawesome/dist/utilities/polyfills/stateset.js:
@home-assistant/webawesome/dist/internal/webawesome-element.js:
@home-assistant/webawesome/dist/internal/webawesome-form-associated-element.js:
@home-assistant/webawesome/dist/styles/component/size.styles.js:
@home-assistant/webawesome/dist/styles/component/variants.styles.js:
@home-assistant/webawesome/dist/translations/en.js:
@home-assistant/webawesome/dist/utilities/localize.js:
@home-assistant/webawesome/dist/events/error.js:
@home-assistant/webawesome/dist/events/load.js:
@home-assistant/webawesome/dist/components/icon/icon.styles.js:
@home-assistant/webawesome/dist/utilities/base-path.js:
@home-assistant/webawesome/dist/components/icon/library.default.js:
@home-assistant/webawesome/dist/components/icon/library.system.js:
@home-assistant/webawesome/dist/components/icon/library.js:
@home-assistant/webawesome/dist/components/icon/icon.js:
@home-assistant/webawesome/dist/components/spinner/spinner.styles.js:
@home-assistant/webawesome/dist/components/spinner/spinner.js:
@home-assistant/webawesome/dist/components/button/button.styles.js:
@home-assistant/webawesome/dist/components/button/button.js:
@home-assistant/webawesome/dist/components/card/card.styles.js:
@home-assistant/webawesome/dist/components/card/card.js:
  (*! Copyright 2026 Fonticons, Inc. - https://webawesome.com/license *)
*/
