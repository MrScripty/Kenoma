"""Controlled finite-K P2/P1 research comparator; never imported by production.
Pressure eliminated exactly from its weak equation. SI, original active law.
"""
import itertools
import numpy as np
from scipy.linalg import cho_factor, cho_solve, solve
from scipy.sparse import coo_matrix
from scipy.optimize import brentq

PARAM = dict(mu=1000., bulk=1e6, kf=20000., b=6., sigma0=8708387.370104775,
             optimumStretch=1., activeWidth=.5)
ACTIVATION = .01
EDGES = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
LENGTHS = np.array([.14,.02,.02])

def quadrature(depth=2):
    a=(5+3*np.sqrt(5))/20; b=(5-np.sqrt(5))/20
    points=np.full((4,4),b); np.fill_diagonal(points,a)
    corners=np.eye(4)
    vertices=np.vstack((corners,[(corners[i]+corners[j])/2 for i,j in EDGES]))
    subtets=np.array([[0,4,5,6],[1,4,7,8],[2,5,7,9],[3,6,8,9],
                     [4,5,6,9],[4,5,7,9],[4,7,8,9],[4,6,8,9]])
    transforms=corners[None]
    for _ in range(depth):
        transforms=np.einsum('tij,sjk->tsik',vertices[subtets],transforms).reshape(-1,4,4)
    # Node recursive implementation uses the same complete point set; ordering immaterial.
    return np.einsum('qi,tij->tqj',points,transforms).reshape(-1,4)

def shape(L):
    L=np.atleast_2d(L); G=np.array([[-1.,-1.,-1.],[1,0,0],[0,1,0],[0,0,1]])
    N=[L[:,i]*(2*L[:,i]-1) for i in range(4)]
    g=[(4*L[:,i,None]-1)*G[i] for i in range(4)]
    for i,j in EDGES:
        N.append(4*L[:,i]*L[:,j]); g.append(4*(L[:,i,None]*G[j]+L[:,j,None]*G[i]))
    return np.stack(N,axis=1),np.stack(g,axis=1)

def mesh(counts):
    counts=np.array(counts); axes=[np.linspace(0,LENGTHS[d],counts[d]+1) for d in range(3)]
    keys=list(itertools.product(*[range(n+1) for n in counts])); ids={k:i for i,k in enumerate(keys)}
    X=[np.array([axes[d][k[d]] for d in range(3)]) for k in keys]; nv=len(X)
    tets=[]
    for lower in itertools.product(*[range(n) for n in counts]):
        for perm in itertools.permutations(range(3)):
            k=np.array(lower); tet=[ids[tuple(k)]]
            for d in perm:
                k=k.copy(); k[d]+=1; tet.append(ids[tuple(k)])
            if np.linalg.det(np.array([X[tet[i]]-X[tet[0]] for i in [1,2,3]]).T)<0:
                tet[1],tet[2]=tet[2],tet[1]
            tets.append(tet)
    mids={}; full=[]
    for tet in tets:
        nodes=tet.copy()
        for i,j in EDGES:
            edge=tuple(sorted((tet[i],tet[j])))
            if edge not in mids:
                mids[edge]=len(X); X.append((X[edge[0]]+X[edge[1]])/2)
            nodes.append(mids[edge])
        full.append(nodes)
    faces={}
    for tet in tets:
        for omitted in range(4):
            face=[tet[i] for i in range(4) if i!=omitted]; key=tuple(sorted(face))
            if key in faces: faces[key]=None
            else: faces[key]=(face,tet[omitted])
    surface=[]
    for record in faces.values():
        if record is None: continue
        face,opposite=record; a,b,c=face
        if np.dot(np.cross(X[b]-X[a],X[c]-X[a]),X[opposite]-X[a])>0: b,c=c,b
        ab=mids[tuple(sorted((a,b)))]; ac=mids[tuple(sorted((a,c)))]; bc=mids[tuple(sorted((b,c)))]
        surface.extend([[a,ab,ac],[b,bc,ab],[c,ac,bc],[ab,bc,ac]])
    X=np.array(X); cap=np.flatnonzero((X[:,0]==0)|(X[:,0]==LENGTHS[0]))
    free=np.setdiff1d(np.arange(3*len(X)),(3*cap[:,None]+np.arange(3)).ravel())
    return dict(X=X,tets=np.array(full),nv=nv,cap=cap,free=free,surface=np.array(surface),counts=counts)

def constitutive(F,p,activation=ACTIVATION,tangent=False):
    """Fixed-pressure P, C and non-volume energy; original normalized axial fiber."""
    J=np.linalg.det(F)
    if not np.isfinite(F).all() or np.any(J<=1e-6): raise ValueError('Positive finite geometry guard')
    G=np.swapaxes(np.linalg.inv(F),-1,-2); I1=np.sum(F*F,axis=(-1,-2)); iso=J**(-2/3)
    f=F[..., :,0]; lam=np.linalg.norm(f,axis=-1); n=f/lam[...,None]
    e=np.maximum(lam-1,0); u=(lam-1)/PARAM['activeWidth']; t=np.clip(u,-1,1)
    curve=np.where(np.abs(u)<1,(1-u*u)**2,0)
    prime=np.where(np.abs(u)<1,-4*u*(1-u*u)/PARAM['activeWidth'],0)
    exp=np.expm1(PARAM['b']*e)
    k=PARAM['kf']/PARAM['b']*exp+activation*PARAM['sigma0']*curve
    kp=np.where(lam>1,PARAM['kf']*np.exp(PARAM['b']*e),0)+activation*PARAM['sigma0']*prime
    P=PARAM['mu']*iso[...,None,None]*(F-I1[...,None,None]/3*G)+p[...,None,None]*G
    P[..., :,0]+=k[...,None]*n
    E=PARAM['mu']/2*(iso*I1-3)+PARAM['kf']/PARAM['b']**2*(exp-PARAM['b']*e)
    E+=activation*PARAM['sigma0']*PARAM['activeWidth']*(t-2*t**3/3+t**5/5)
    if not np.isfinite(P).all() or not np.isfinite(E).all(): raise ValueError('Material finite guard')
    C=None
    if tangent:
        C=np.empty(F.shape[:-2]+(3,3,3,3))
        for r,a,s,b in itertools.product(range(3),repeat=4):
            C[...,r,a,s,b]=PARAM['mu']*iso*((r==s and a==b)-2/3*F[...,s,b]*G[...,r,a]
                +I1/3*G[...,r,b]*G[...,s,a]-2/3*G[...,s,b]*(F[...,r,a]-I1/3*G[...,r,a]))
            C[...,r,a,s,b]-=p*G[...,r,b]*G[...,s,a]
            if a==0 and b==0:
                C[...,r,a,s,b]+=kp*n[...,r]*n[...,s]+k/lam*((r==s)-n[...,r]*n[...,s])
    return P,C,E,J,G,lam

class Body:
    def __init__(self,m,depth=2):
        self.m=m; self.L=quadrature(depth); self.depth=depth
        _,g=shape(self.L); X=m['X'][m['tets']]
        jac=np.einsum('eni,qna->eqia',X,g); det=np.linalg.det(jac)
        if np.any(det<=1e-15): raise ValueError('Reference determinant guard')
        self.grad=np.einsum('qna,eqai->eqni',g,np.linalg.inv(jac))
        self.w=det/(6*len(self.L)); self.volume=self.w.sum(); self.pi=m['tets'][:,:4]
        self.di=(3*m['tets'][...,None]+np.arange(3)).reshape(-1,30)
        Mloc=np.einsum('qi,qj,eq->eij',self.L,self.L,self.w)
        self.M=self.assemble(Mloc,self.pi,self.pi,m['nv'],m['nv']).toarray()
        self.Mfactor=cho_factor(self.M)
        scalar=np.einsum('eqna,eqma,eq->enm',self.grad,self.grad,self.w)
        Aloc=np.einsum('enm,ij->enimj',scalar,np.eye(3)).reshape(-1,30,30)
        self.A=self.assemble(Aloc,self.di,self.di,3*len(m['X']),3*len(m['X']))
        _,cg=shape(np.eye(4)); cjac=np.einsum('eni,qna->eqia',X,cg)
        self.cornergrad=np.einsum('qna,eqai->eqni',cg,np.linalg.inv(cjac))
    @staticmethod
    def assemble(local,rows,cols,nr,nc):
        rr=np.broadcast_to(rows[:,:,None],local.shape).ravel()
        cc=np.broadcast_to(cols[:,None,:],local.shape).ravel()
        return coo_matrix((local.ravel(),(rr,cc)),shape=(nr,nc)).tocsr()
    def evaluate(self,x,hessian=False):
        X=x[self.m['tets']]; F=np.einsum('eni,eqna->eqia',X,self.grad)
        J=np.linalg.det(F)
        if np.any(J<=1e-6) or not np.isfinite(J).all(): raise ValueError('Positive finite geometry guard')
        log=np.log(J); bloc=np.einsum('qi,eq,eq->ei',self.L,log,self.w)
        b=np.zeros(self.m['nv']); np.add.at(b,self.pi,bloc)
        p=PARAM['bulk']*cho_solve(self.Mfactor,b); pq=p[self.pi]@self.L.T
        P,C,E,J,G,lam=constitutive(F,pq,tangent=hessian)
        gloc=np.einsum('eqia,eqna,eq->eni',P,self.grad,self.w).reshape(-1,30)
        g=np.zeros(x.size); np.add.at(g,self.di,gloc)
        Dloc=np.einsum('qv,eqia,eqna,eq->evni',self.L,G,self.grad,self.w).reshape(-1,4,30)
        D=self.assemble(Dloc,self.pi,self.di,self.m['nv'],x.size)
        H=None
        if hessian:
            Hloc=np.empty((len(X),30,30))
            for e in range(len(X)):
                Hloc[e]=np.einsum('qna,qiajb,qmb,q->nimj',self.grad[e],C[e],self.grad[e],self.w[e],optimize=True).reshape(30,30)
            Huu=self.assemble(Hloc,self.di,self.di,x.size,x.size)
            f=self.m['free']; Df=D[:,f].toarray()
            H=Huu[f][:,f].toarray()+PARAM['bulk']*Df.T@cho_solve(self.Mfactor,Df)
        corner=np.linalg.det(np.einsum('eni,eqna->eqia',X,self.cornergrad))
        weak=b-self.M@p/PARAM['bulk']; mismatch=log-pq/PARAM['bulk']
        return dict(g=g,p=p,b=b,D=D,H=H,energy=float(np.sum(E*self.w)+.5*p@b),
            residual=float(np.linalg.norm(g[self.m['free']])),
            weakRMS=float(np.sqrt(max(0,weak@cho_solve(self.Mfactor,weak)/self.volume))),
            pointwiseRMS=float(np.sqrt(np.sum(mismatch*mismatch*self.w)/self.volume)),
            Jmin=float(min(J.min(),corner.min())),Jmax=float(max(J.max(),corner.max())),
            lamMin=float(lam.min()),lamMax=float(lam.max()))
    def analytic(self,stretch):
        def lateral(s):
            F=np.diag([stretch,s,s])[None]; p=PARAM['bulk']*np.log(np.linalg.det(F))
            return constitutive(F,p)[0][0,1,1]
        s=brentq(lateral,.6,1.2,xtol=1e-14,rtol=1e-14,maxiter=80)
        F=np.diag([stretch,s,s])[None]; p=PARAM['bulk']*np.log(np.linalg.det(F))
        P=constitutive(F,p)[0][0]
        return self.m['X']*np.array([stretch,s,s]),dict(transverseStretch=s,J=float(np.linalg.det(F)[0]),
            pressurePa=float(p[0]),capForceN=float(P[0,0]*LENGTHS[1]*LENGTHS[2]))
    def initial(self,stretch):
        x,analytic=self.analytic(stretch); start=x.copy()
        if stretch!=1:
            t=self.m['X']/LENGTHS; wave=np.sin(np.pi*t[:,0])*np.sin(np.pi*t[:,1])*np.sin(np.pi*t[:,2])
            start+=1e-5*wave[:,None]*np.stack([.3*np.cos(np.pi*t[:,0]),np.ones(len(t)),.37*np.cos(2*np.pi*t[:,0])],axis=1)
            start[self.m['cap']]=x[self.m['cap']]
        return start,x,analytic
    def newton(self,start):
        x=start.copy(); f=self.m['free']; history=[]; reason='Iteration budget exhausted'
        for it in range(81):
            state=self.evaluate(x,hessian=True); g=state['g'][f]; norm=np.linalg.norm(g)
            history.append(dict(iteration=it,forceResidualN=float(norm),pointwisePressureRMS=state['pointwiseRMS'],
                                Jmin=state['Jmin'],Jmax=state['Jmax']))
            if norm<=1e-4: return x,state,history,'Stationary force gate passed'
            if it==80: break
            direction=solve(state['H'],-g,assume_a='sym')
            linear=np.linalg.norm(state['H']@direction+g)/norm
            history[-1]['linearRelativeResidual']=float(linear)
            if not np.isfinite(direction).all() or linear>1e-10:
                reason='True tangent linear residual rejected'; break
            accepted=False
            for back in range(24):
                alpha=2.**(-back); trial=x.copy(); trial.ravel()[f]+=alpha*direction
                try: q=self.evaluate(trial)
                except ValueError: continue
                if q['residual']**2 <= (1-2e-4*alpha)*norm**2:
                    x=trial; accepted=True; history[-1]['stepFraction']=alpha; break
            if not accepted: reason='Residual line search rejected'; break
        return x,self.evaluate(x,hessian=True),history,reason
